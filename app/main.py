from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.routers import inventory_item

app = FastAPI()
router = APIRouter()

# CORS Config - update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registrations
app.include_router(inventory_item.router)

# Root Route
@app.get("/")
async def read_root():
    return {"Message": "Hello World. I am home."}