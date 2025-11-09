from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, List
import bcrypt
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

from app.database import db, connect_to_mongo, close_mongo_connection
from app.models import UserCreate, UserLogin, JournalCreate, JournalResponse

app = FastAPI(title="Journal 360")


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()

# JWT Settings
SECRET_KEY = "asdgsdfgsdfg"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


# API Routes
@app.post("/api/signup")
async def signup(user: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "email": user.email,
        "username": user.username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "User created successfully"
    }


@app.post("/api/login")
async def login(user: UserLogin):
    # Find user
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }


@app.get("/api/journals", response_model=List[JournalResponse])
async def get_journals(current_user: dict = Depends(get_current_user)):
    journals = []
    cursor = db.journals.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)
    
    async for journal in cursor:
        journals.append({
            "id": str(journal["_id"]),
            "title": journal["title"],
            "content": journal["content"],
            "created_at": journal["created_at"],
            "updated_at": journal.get("updated_at", journal["created_at"])
        })
    
    return journals


@app.post("/api/journals", response_model=JournalResponse)
async def create_journal(journal: JournalCreate, current_user: dict = Depends(get_current_user)):
    journal_dict = {
        "user_id": str(current_user["_id"]),
        "title": journal.title,
        "content": journal.content,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.journals.insert_one(journal_dict)
    
    return {
        "id": str(result.inserted_id),
        "title": journal.title,
        "content": journal.content,
        "created_at": journal_dict["created_at"],
        "updated_at": journal_dict["updated_at"]
    }


@app.put("/api/journals/{journal_id}", response_model=JournalResponse)
async def update_journal(journal_id: str, journal: JournalCreate, current_user: dict = Depends(get_current_user)):
    try:
        obj_id = ObjectId(journal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid journal ID")
    
    # Check if journal exists and belongs to user
    existing_journal = await db.journals.find_one({
        "_id": obj_id,
        "user_id": str(current_user["_id"])
    })
    
    if not existing_journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    
    # Update journal
    update_data = {
        "title": journal.title,
        "content": journal.content,
        "updated_at": datetime.utcnow()
    }
    
    await db.journals.update_one({"_id": obj_id}, {"$set": update_data})
    
    return {
        "id": journal_id,
        "title": journal.title,
        "content": journal.content,
        "created_at": existing_journal["created_at"],
        "updated_at": update_data["updated_at"]
    }


@app.delete("/api/journals/{journal_id}")
async def delete_journal(journal_id: str, current_user: dict = Depends(get_current_user)):
    try:
        obj_id = ObjectId(journal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid journal ID")
    
    # Check if journal exists and belongs to user
    result = await db.journals.delete_one({
        "_id": obj_id,
        "user_id": str(current_user["_id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Journal not found")
    
    return {"message": "Journal deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

