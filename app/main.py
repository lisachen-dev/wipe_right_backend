from fastapi import FastAPI, APIRouter, Header
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    address,
    booking,
    customer,
    inventory_item,
    provider,
    provider_inventory,
    review,
    service,
    service_inventory,
    status_update,
    transaction
)

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
app.include_router(address.router)
app.include_router(booking.router)
app.include_router(customer.router)
app.include_router(inventory_item.router)
app.include_router(provider.router)
app.include_router(provider_inventory.router)
app.include_router(review.router)
app.include_router(service.router)
app.include_router(service_inventory.router)
app.include_router(status_update.router)
app.include_router(transaction.router)

# Root Route routes to swagger api for now
@app.get("/docs")
async def read_root():
    return {"Message": "Hello World. I am home."}