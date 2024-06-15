from fastapi import FastAPI
from config.db import engine, Base
from routes import news

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Configurar FastAPI
app = FastAPI()

# Incluir rutas
app.include_router(news.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)