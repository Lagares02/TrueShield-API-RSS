from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from config.db import get_db
from services.news import buscar_y_guardar_noticias, get_news_by_category, contrasting_rss
from models.models import MainNew

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    num_noticias = db.query(MainNew).count()
    return templates.TemplateResponse("index.html", {"request": request, "num_noticias": num_noticias})

@router.post("/validate_prompt")
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

@router.post("/save_news")
async def guardar_noticias(db: Session = Depends(get_db)):
    num_noticias_guardadas = buscar_y_guardar_noticias(db)
    message = f"{num_noticias_guardadas} noticias guardadas correctamente"
    return {"message": message, "num_noticias": num_noticias_guardadas}

@router.get("/news_by_category")
async def news_by_category(db: Session = Depends(get_db)):
    categories_news = get_news_by_category(db)
    return categories_news

@router.post("/contrasting", response_model=dict)
async def contrasting(data: dict, db: Session = Depends(get_db)):
    try:
        keywords = data.get("keywords")
        subjects = data.get("subjects")

        matched_news = contrasting_rss(db, keywords, subjects)

        return {"News": matched_news}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))