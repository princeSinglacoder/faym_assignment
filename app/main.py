from fastapi import FastAPI
from app.database.database import engine, Base
# Import models to register them on Base.metadata
from app.models.user import User
from app.models.sale import Sale
from app.models.withdrawal import Withdrawal

# Create database tables
print("Creating tables in the database...")
Base.metadata.create_all(bind=engine)
print("Registered tables on Base.metadata:", list(Base.metadata.tables.keys()))


app = FastAPI(title="Faym Affiliate Payout Management System")

from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Faym Assessment API is live!"}

