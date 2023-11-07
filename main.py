from fastapi import FastAPI, Form, UploadFile, File
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from asyncpg import create_pool
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from uuid import uuid4
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

# FastAPI application
app = FastAPI()

# PostgreSQL database connection
DATABASE_URL = "postgresql://username:password@localhost/database"
pg_db = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB database connection
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
mongo_db = mongo_client["user_db"]
collection = mongo_db["users"]

# SQLAlchemy model
Base = declarative_base()

class PostgresUser(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)

# Pydantic model for registration
class Registration(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: UploadFile = File(...)

# Registration endpoint
@app.post("/register/")
async def register_user(registration: Registration, request: Request):
    # Check if email already exists in PostgreSQL
    async with pg_db.transaction():
        query = PostgresUser.__table__.select().where(PostgresUser.email == registration.email)
        user = await pg_db.fetch_one(query)
        if user:
            return JSONResponse(content={"message": "Email already exists"}, status_code=400)

    # Generate a unique user_id for both databases
    user_id = str(uuid4())

    # Store user data in PostgreSQL
    async with pg_db.transaction():
        query = PostgresUser.__table__.insert().values(
            user_id=user_id,
            first_name=registration.full_name.split()[0],
            email=registration.email,
            phone=registration.phone,
            password=registration.password,
        )
        await pg_db.execute(query)

    # Store profile picture in MongoDB
    profile_picture_bytes = await registration.profile_picture.read()
    await request.app.mongodb.save_file(user_id, profile_picture_bytes)

    return JSONResponse(content={"message": "User registered successfully"})

# GET method for user details
@app.get("/user/{user_id}")
async def get_user_details(user_id: str):
    # Retrieve user details from PostgreSQL
    async with pg_db.transaction():
        query = PostgresUser.__table__.select().where(PostgresUser.user_id == user_id)
        user = await pg_db.fetch_one(query)

    if user:
        # Retrieve profile picture from MongoDB
        file_data = await request.app.mongodb.get_file(user_id)

        if file_data:
            return {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "email": user.email,
                "phone": user.phone,
                "profile_picture": file_data
            }
    return JSONResponse(content={"message": "User not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.middleware.cors import CORSMiddleware

    # Set up CORS to allow requests from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up MongoDB file operations
    app.mongodb = mongo_db

    # Start the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
