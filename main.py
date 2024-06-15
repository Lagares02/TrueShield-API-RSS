import feedparser
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()
# Configuración de la base de datos
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:5432/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarar el modelo
Base = declarative_base()

# Crear la tabla si no existe
Base.metadata.create_all(bind=engine)

class MainNew(Base):
    __tablename__ = 'main_new'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    body = Column(Text)
    link_article = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    media_id = Column(Integer, ForeignKey('main_media.id'))

class MainRssUrl(Base):
    __tablename__ = 'main_rss_url'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    rss = Column(String, nullable=False)
    media_id = Column(Integer, ForeignKey('main_media.id'))
    media = relationship('MainMedia', back_populates='rss_urls')

class MainMedia(Base):
    __tablename__ = 'main_media'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    country = Column(String)
    web = Column(String)
    logo = Column(String)
    rss_urls = relationship('MainRssUrl', back_populates='media')
    news = relationship('MainNew', backref='media')

# Configurar FastAPI
app = FastAPI()

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Función para buscar y guardar noticias en la base de datos a través de las RSS
def buscar_y_guardar_noticias():
    num_noticias_guardadas = 0
    db = SessionLocal()
    for rss_url in db.query(MainRssUrl).all():
        feed = feedparser.parse(rss_url.rss)
        category= rss_url.category
        print(category)
        print("num noticias: de ",rss_url.rss," ",len(feed))
        for entry in feed.entries:
            # en casi si todo se da bien 
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

            # en caso que falte algo y todo se rompa 
            except AttributeError or KeyError:
                print("falto algo")
                continue

    # Hacer commit fuera del bucle para mejorar el rendimiento
    db.commit()
    db.close()

    return num_noticias_guardadas

# Función para obtener todas las noticias por categoría
def get_news_by_category():
    categories_news = {}
    db = SessionLocal()
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
    
    db.close()
    return categories_news

# Ruta para renderizar el index.html
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    num_noticias = SessionLocal().query(MainNew).count()
    return templates.TemplateResponse("index.html", {"request": request, "num_noticias": num_noticias})

# Ruta para manejar la solicitud de validar el titular de la noticia
@app.post("/validate_prompt")
async def validar_titular(data: dict):
    titular_usuario = data.get('titular_usuario')
    if titular_usuario:
        num_noticias = SessionLocal().query(MainNew).filter(MainNew.title.ilike(f'%{titular_usuario}%')).count()
        if num_noticias > 0:
            return {"message": "Si se encuentra la noticia."}
        else:
            raise HTTPException(status_code=404, detail="No se encontró ninguna noticia con ese titular.")
    else:
        raise HTTPException(status_code=400, detail="No se proporcionó un titular válido.")

# Ruta para manejar la solicitud de guardar noticias
@app.post("/save_news")
async def guardar_noticias():
    num_noticias_guardadas = buscar_y_guardar_noticias()
    message = f"{num_noticias_guardadas} noticias guardadas correctamente"
    return {"message": message, "num_noticias": num_noticias_guardadas}

# Ruta para obtener todas las noticias por categoría
@app.get("/news_by_category")
async def news_by_category():
    categories_news = get_news_by_category()
    return categories_news


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)