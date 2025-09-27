from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, children, stories

app = FastAPI(
    title="LumosReading API",
    description="AI-Powered Children's Reading Platform with Neurodiversity Support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)
app.include_router(children.router)
app.include_router(stories.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LumosReading API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "lumosreading-api"}
