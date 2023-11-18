from fastapi import FastAPI, HTTPException, Depends, security
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

from schema import UserCreate, User, LeadCreate, Lead
import services

app = FastAPI()

@app.get("/api/all_users")
async def get_users(db : Session = Depends(services.get_db)):
    return await services.get_all_user(db)

@app.post("/api/users")
async def create_user(user : UserCreate, db : Session = Depends(services.get_db)):
    
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code = 400, detail = "Email already exists")
    
    user = await services.create_user(user, db)

    return await services.create_token(user)

@app.post("/api/token")
async def generate_token(form_data: security.OAuth2PasswordRequestForm = Depends(), db : Session = Depends(services.get_db)):
    
    user = await services.autheticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code = 401, detail = "Invalid Credentials")
    
    return await services.create_token(user)

@app.get("/api/users/me", response_model = User)
async def get_user(user : User = Depends(services.get_current_user)):
    return user

@app.post("/api/leads", response_model = Lead)
async def create_lead(lead: LeadCreate, user : User = Depends(services.get_current_user), db : Session = Depends(services.get_db)):
    return await services.create_lead(user = user, lead = lead, db = db)

@app.get("/api/leads", response_model = List[Lead])
async def get_leads(user : User = Depends(services.get_current_user), db : Session = Depends(services.get_db)):
    return await services.get_leads(user = user, db = db)

@app.get("/api/leads/{lead_id}", status_code = 200)
async def get_lead(lead_id : int, user : User = Depends(services.get_current_user), db : Session = Depends(services.get_db)):
    return await services.get_lead(lead_id = lead_id, user = user, db = db)

@app.delete("/api/leads/{lead_id}", status_code = 204)
async def delete_lead(lead_id : int, user : User = Depends(services.get_current_user), db : Session = Depends(services.get_db)):
    await services.delete_lead(lead_id, user,  db)
    return dict(message = "Successfully Deleted")

@app.put("/api/leads/{lead_id}", status_code = 200)
async def update_lead(lead_id : int, lead : LeadCreate, user : User = Depends(services.get_current_user), db : Session = Depends(services.get_db)):
    await services.update_lead(lead_id, lead, user,  db)
    return dict(message = "Successfully Updated")

@app.get("/api")
async def root():
    return dict(message = "Test String")
