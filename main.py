from fastapi import FastAPI, WebSocket, Depends
from config.db import engine, Base
from routes import news
from sqlalchemy.orm import Session
from config.db import get_db
import json

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Configurar FastAPI
app = FastAPI()

# Incluir rutas
app.include_router(news.router)

@app.websocket("/contrasting")
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
                "item": items
            }
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)