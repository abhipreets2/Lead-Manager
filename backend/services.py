import database
from sqlalchemy.orm import Session
from models import User, Lead
import schema
from passlib import hash
import jwt
from fastapi import security, Depends, HTTPException
import datetime

oauth2schema = security.OAuth2PasswordBearer(tokenUrl = "/api/token")
JWT_SECRET  = 'myjwtsecret'

def create_database():
    return database.Base.metadata.create_all(bind = database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_email(email : str, db : Session):
    return db.query(User).filter(User.email == email).first()

async def create_user(user : schema.UserCreate, db : Session):
    
    user_obj = User(email = user.email, hashed_password = hash.bcrypt.hash(user.hashed_password))
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def autheticate_user(email : str, password : str, db : Session):
    user = await get_user_by_email(email, db)

    if not user:
        return False
    
    if not user.verify_password(password):
        return False
    
    return user

async def create_token(user : User):

    user_obj = schema.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token = token, token_type = "bearer")

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2schema)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(User).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )
    
    return schema.User.from_orm(user)

async def create_lead(user : schema.User, lead: schema.LeadCreate, db : Session):
    lead = Lead(**lead.dict(), owner_id = user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return schema.Lead.from_orm(lead)

async def get_leads(user : schema.User, db : Session):
    leads = db.query(Lead).filter_by(owner_id = user.id)

    return list(map(schema.Lead.from_orm, leads))

async def _lead_selector(lead_id : int, user : schema.User, db : Session):
    lead = db.query(Lead).filter_by(owner_id = user.id).filter(Lead.id == lead_id).first()

    if lead is None:
        raise HTTPException(status_code = 404, detail = "Lead does not exist")

    return lead

async def get_lead(lead_id : int, user : schema.User, db : Session):
    lead = await _lead_selector(lead_id = lead_id, user = user, db = db)

    return schema.Lead.from_orm(lead)

async def delete_lead(lead_id : int, user : schema.User, db : Session):
    lead = await _lead_selector(lead_id, user, db)

    db.delete(lead)
    db.commit()

async def update_lead(lead_id : int, lead : schema.LeadCreate, user : schema.User, db : Session):
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = datetime.datetime.utcnow()

    db.commit()
    db.refresh(lead_db)

    return schema.Lead.from_orm(lead_db)





