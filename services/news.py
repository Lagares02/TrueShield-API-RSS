import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
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
                print("faltó algo")
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