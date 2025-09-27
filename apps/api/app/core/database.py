from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import Generator

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lumos:lumos_dev_2024@localhost:5432/lumosreading")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # 开发环境使用NullPool
    echo=True if os.getenv("DEBUG") == "true" else False,
    future=True
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

def get_db() -> Generator:
    """
    数据库依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
