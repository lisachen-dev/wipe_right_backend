from dotenv import load_dotenv
from sqlmodel import create_engine
import os

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)