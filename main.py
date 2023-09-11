from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Replace these with your PostgreSQL connection details
DATABASE_URL = "postgresql://username:password@localhost/dbname"

# Create the FastAPI app
app = FastAPI()

# SQLAlchemy database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define SQLAlchemy models for User and Profile
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Pydantic models for request and response
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str

# User registration route
@app.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate):
    db = SessionLocal()
    
    # Check if email or phone already exist
    existing_user_email = db.query(User).filter(User.email == user.email).first()
    existing_user_phone = db.query(User).filter(User.phone == user.phone).first()
    
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if existing_user_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    
    return db_user

# Get user details route
@app.get("/user/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
