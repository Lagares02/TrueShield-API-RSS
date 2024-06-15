import feedparser
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from config.db import engine, get_db, Base
from models.models import MainNew, MainRssUrl

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Configurar FastAPI
app = FastAPI()

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Función para buscar y guardar noticias en la base de datos a través de las RSS
def buscar_y_guardar_noticias(db: Session):
    num_noticias_guardadas = 0
    for rss_url in db.query(MainRssUrl).all():
        feed = feedparser.parse(rss_url.rss)
        category = rss_url.category
        print(category)
        print("num noticias: de ", rss_url.rss, " ", len(feed))
        for entry in feed.entries:
            try:
                # Verificar si la noticia ya existe en la base de datos
                existing_news = db.query(MainNew).filter_by(title=entry.title).first()
                if existing_news:
                    continue

                # Crear un nuevo registro de noticia
                new_news = MainNew(
                    title=entry.title,
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

            except AttributeError or KeyError:
                print("faltó algo")
                continue

    # Hacer commit fuera del bucle para mejorar el rendimiento
    db.commit()

    return num_noticias_guardadas

# Función para obtener todas las noticias por categoría
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

# Ruta para renderizar el index.html
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    num_noticias = db.query(MainNew).count()
    return templates.TemplateResponse("index.html", {"request": request, "num_noticias": num_noticias})

# Ruta para manejar la solicitud de validar el titular de la noticia
@app.post("/validate_prompt")
async def validar_titular(data: dict, db: Session = Depends(get_db)):
    titular_usuario = data.get('titular_usuario')
    if titular_usuario:
        num_noticias = db.query(MainNew).filter(MainNew.title.ilike(f'%{titular_usuario}%')).count()
        if num_noticias > 0:
            return {"message": "Si se encuentra la noticia."}
        else:
            raise HTTPException(status_code=404, detail="No se encontró ninguna noticia con ese titular.")
    else:
        raise HTTPException(status_code=400, detail="No se proporcionó un titular válido.")

# Ruta para manejar la solicitud de guardar noticias
@app.post("/save_news")
async def guardar_noticias(db: Session = Depends(get_db)):
    num_noticias_guardadas = buscar_y_guardar_noticias(db)
    message = f"{num_noticias_guardadas} noticias guardadas correctamente"
    return {"message": message, "num_noticias": num_noticias_guardadas}

# Ruta para obtener todas las noticias por categoría
@app.get("/news_by_category")
async def news_by_category(db: Session = Depends(get_db)):
    categories_news = get_news_by_category(db)
    return categories_news

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)