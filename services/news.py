import feedparser
from datetime import datetime
import time
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError
from models.models import MainNew, MainRssUrl
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

def truncate_string(value, max_length):
    if value and len(value) > max_length:
        return value[:max_length]
    return value

def procesar_feed(db: Session, rss_url):
    num_noticias_guardadas = 0
    feed = feedparser.parse(rss_url.rss)
    category = rss_url.category
    print(category)
    print("num noticias: ", len(feed.entries), " de ", rss_url.rss)
    for entry in feed.entries:
        try:
            # Truncate title, summary, body, and authors if they are too long
            title = truncate_string(entry.title, 200)
            summary = truncate_string(
                getattr(entry, 'description', None) or getattr(entry, 'summary', None) or "", 200)
            body = truncate_string(getattr(entry, 'body', None) or "", 200)
            authors = truncate_string(getattr(entry, 'author', None) or getattr(entry, 'creator', None) or "", 200)
            link = truncate_string(getattr(entry, 'link', None) or "", 200)

            # Verificar si la noticia ya existe en la base de datos
            existing_news = db.query(MainNew).filter_by(title=title).first()
            if existing_news:
                continue

            # Crear un nuevo registro de noticia
            new_news = MainNew(
                title=title,
                summary=summary,
                body=body,
                link_article=link,
                publication_date=datetime.now(),
                media_id=rss_url.media_id,
                authors=authors
            )

            # Verificar si el feed tiene la fecha de actualización (updated_parsed)
            if hasattr(entry, 'updated_parsed'):
                new_news.publication_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))

            # Guardar la nueva noticia en la base de datos
            db.add(new_news)
            num_noticias_guardadas += 1

        except (AttributeError, KeyError) as e:
            print(f"Error: {e}")
            continue

    return num_noticias_guardadas

def buscar_y_guardar_noticias(db: Session):
    num_noticias_guardadas_total = 0
    num_threads = os.cpu_count() * 2
    try:
        rss_urls = db.query(MainRssUrl).all()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(procesar_feed, db, rss_url): rss_url for rss_url in rss_urls}
            for future in as_completed(futures):
                try:
                    num_noticias_guardadas = future.result()
                    num_noticias_guardadas_total += num_noticias_guardadas
                except Exception as e:
                    print(f"Error procesando el feed: {e}")
        
        # Hacer commit fuera del bucle para mejorar el rendimiento
        db.commit()

    except SQLAlchemyError as e:
        print(f"Error de SQLAlchemy: {e}")
        db.rollback()  # Rollback en caso de error
        num_noticias_guardadas_total = 0  # Reiniciar contador si hay errores

    return num_noticias_guardadas_total

def get_news_by_category(db: Session):
    categories_news = {}
    for rss_url in db.query(MainRssUrl).all():
        category = rss_url.category
        if category not in categories_news:
            categories_news[category] = []

        media_id = rss_url.media_id
        news = db.query(MainNew).filter(MainNew.media_id == media_id).all()

        for new in news:
            new_dict = {
                "title": new.title,
                "summary": new.summary,
                "body": new.body,
                "publication_date": new.publication_date,
                "url": new.link_article,
                "authors": new.authors
            }
            categories_news[category].append(new_dict)

    return categories_news
    
def contrasting_rss(db: Session, keywords = [], subjects = []):
    try:
        # List to store matched news
        matched_news = []

        # Query all news from database with related media information
        news_query = db.query(MainNew).options(
            selectinload(MainNew.media)
        )

        for news in news_query:
            match_score = 0

            # Split title and summary into words
            title_words = news.title.lower().split()
            summary_words = news.summary.lower().split()
            
            # keywords and subjects lower
            keywords_lower = list(map(lambda x: x.lower(), keywords))
            subjects_lower = list(map(lambda x: x.lower(), subjects))

            # Compare keywords and subjects with title and summary
            for keyword in keywords_lower + subjects_lower:
                if (keyword in title_words or
                    keyword in summary_words):
                    match_score += 1
                    
            if match_score >= 1:
                Domain = round(float(match_score / (len(keywords_lower) + len(subjects_lower))), 2)
            else:
                Domain = 0.0
            
            # Minimum of 2 matches required for the news to be considered
            if match_score >= 2:
                matched_news.append({
                    "Id": news.id,
                    "Page": news.media.name,
                    "DatePublication": news.publication_date.strftime('%Y-%m-%d'),
                    "Title": news.title,
                    "Summary": news.summary,
                    "BodyText": news.body,
                    "Authors": news.authors,
                    "Confidence": 0.60,
                    "Domain": Domain,
                    "Inference": random.choice(["affirmation", "assumption", "denial"]),
                    "Type_item": "Rss"
                })
        
        # Sort matched_news by match_score (descending)
        matched_news = sorted(matched_news, key=lambda x: x.get("match_score", 0), reverse=True)
        
        print(matched_news)

        return matched_news

    except Exception as e:
        raise e