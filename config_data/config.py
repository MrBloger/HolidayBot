import os
from pathlib import Path
from dotenv import load_dotenv

from dataclasses import dataclass
from sqlalchemy.engine import URL


@dataclass
class settings:
    BASE_URl = Path(__file__).parent.parent.resolve()
    
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = str(os.getenv('DB_PORT'))
    DB_USER: str = os.getenv('DB_USER')
    DB_PASS: str = os.getenv('DB_PASS')
    DB_NAME: str = os.getenv('DB_NAME')
    
    
def get_db_url():
    return URL.create(
        drivername='postgresql+asyncpg',
        username=settings.DB_USER,
        password=settings.DB_PASS,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME
)



