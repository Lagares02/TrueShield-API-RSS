import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.models import MainNew, MainRssUrl

def buscar_y_guardar_noticias(db: Session):
    num_noticias_guardadas = 0
    for rss_url in db.query(MainRssUrl).all():
        feed = feedparser.parse(rss_url.rss)
        category = rss_url.category
        print(category)
        print("num noticias: de ", rss_url.rss, " ", len(feed))
        for entry in feed.entries:
            try:
                # Verificar si la longitud del título es mayor a 200 caracteres y truncar si es necesario
                title = entry.title if len(entry.title) <= 200 else entry.title[:200]

                # Verificar si la noticia ya existe en la base de datos
                existing_news = db.query(MainNew).filter_by(title=title).first()
                if existing_news:
                    continue

                # Crear un nuevo registro de noticia
                new_news = MainNew(
                    title=title,
                    summary=entry.summary,
                    link_article=entry.link,
                    publication_date=datetime.now(),
                    media_id=rss_url.media_id,
                )

                # Verificar si el feed tiene la fecha de actualización (updated_parsed)
                if hasattr(feed, 'updated_parsed'):
                    new_news.publication_date = datetime.fromtimestamp(feed.updated_parsed)

                # Verificar si la noticia tiene el cuerpo (body)
                if hasattr(entry, 'body') and entry.body:
                    new_news.body = entry.body
                else:
                    new_news.body = "No hay cuerpo disponible."

                # Guardar la nueva noticia en la base de datos
                db.add(new_news)
                num_noticias_guardadas += 1

            except (AttributeError, KeyError):
                print("Faltó algo")
                continue

    # Hacer commit fuera del bucle para mejorar el rendimiento
    db.commit()
    return num_noticias_guardadas

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
            }
            categories_news[category].append(new_dict)

    return categories_news
    
def contrasting_rss(db: Session, keywords: list, subjects: list):
    try:
        # List to store matched news
        matched_news = []

        # Query all news from database
        news_query = db.query(MainNew)

        for news in news_query:
            match_score = 0

            # Split title and summary into words
            title_words = news.title.lower().split()
            summary_words = news.summary.lower().split()

            # Compare keywords and subjects with title and summary
            for keyword in keywords + subjects:
                if (keyword in title_words or
                    keyword in summary_words):
                    match_score += 1

            # Minimum of 3 matches required for the news to be considered
            if match_score >= 3:
                matched_news.append({
                    "Id": news.id,
                    "Page": news.media_id,
                    "DatePublication": news.publication_date.strftime('%Y-%m-%d'),
                    "Title": news.title,
                    "Summary": news.summary,
                    "BodyText": news.body,
                    "TrueLevel": 0.6 # Nivel de veracidad establecido (de 0.0 hasta 1.0)
                })

        # Sort matched_news by match_score (descending)
        matched_news = sorted(matched_news, key=lambda x: x.get("match_score", 0), reverse=True)

        return matched_news

    except Exception as e:
        raise e