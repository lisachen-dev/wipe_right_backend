from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routers import (
    address,
    auth_routes,
    booking,
    customer,
    inventory_item,
    provider,
    provider_inventory,
    review,
    service,
    service_inventory,
    status_update,
    transaction,
    user_profile,
)

app = FastAPI()
router = APIRouter()

# TODO CORS Config - update for production
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registrations
app.include_router(address.router)
app.include_router(auth_routes.router)
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
app.include_router(user_profile.router)


# Root Route redirects to Swagger docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
