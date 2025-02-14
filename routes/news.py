from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from config.db import get_db
from services.news import buscar_y_guardar_noticias, get_news_by_category, contrasting_rss
from models.models import MainNew
import json

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


@router.post("/contrasting_rss", response_model=dict)
async def contrasting(data: dict, db: Session = Depends(get_db)):
    try:
        print("recibido!!!")
        Keywords = data.get("keywords", {}).get("keywords_es", [])
        Subjects = data.get("subjects", [])
        prompt = data.get("prompt") # Para la inferencia
        
        matched_news = contrasting_rss(db, Keywords, Subjects)

        return {"Rss": matched_news}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/contrasting")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    print("WebSocket connection established")
    
    try:
        data = await websocket.receive_text()
        print(f"Texto recibido: {data}")
        message = json.loads(data)
        print(f"Message transformado a JSON: {message}")
        
        Keywords = message.get("keywords")
        Subjects = message.get("subjects")
        
        while True:
            
            items = contrasting_rss(db, Keywords, Subjects)
            
            return {
                "Rss": items
            }
        
    except Exception as e:
        print(f"Connection error: {e}")