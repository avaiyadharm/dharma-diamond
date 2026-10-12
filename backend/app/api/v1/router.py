from fastapi import APIRouter
from app.api.v1 import (
    auth, diamonds, jewellery, gemstones, purchases,
    sales, parties, inventory, invoices, payments,
    dashboard, reports, audit
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(diamonds.router)
api_router.include_router(jewellery.router)
api_router.include_router(gemstones.router)
api_router.include_router(purchases.router)
api_router.include_router(sales.router)
api_router.include_router(parties.router)
api_router.include_router(inventory.router)
api_router.include_router(invoices.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
