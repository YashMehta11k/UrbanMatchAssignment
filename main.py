from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from typing import List
import json

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.dict()
    user_dict["_interests"] = json.dumps(user_dict.pop("interests"))
    db_user = models.User(**user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    
    if "interests" in update_data:
        db_user._interests = json.dumps(update_data.pop("interests"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None

@app.get("/users/{user_id}/matches", response_model=List[schemas.MatchResponse])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    potential_matches = db.query(models.User).filter(
        models.User.gender != user.gender,
        models.User.id != user_id
    ).all()
    
    matches = []
    user_interests = set(user.interests)
    
    for match in potential_matches:
        match_interests = set(match.interests)
        common_interests = len(user_interests.intersection(match_interests))
        total_interests = len(user_interests.union(match_interests))
        
        interest_score = common_interests / total_interests if total_interests > 0 else 0
        age_difference_score = 1 - (abs(user.age - match.age) / 50) 
        city_score = 1 if user.city.lower() == match.city.lower() else 0
        
        compatibility_score = (
            interest_score * 0.5 +
            age_difference_score * 0.3 +
            city_score * 0.2
        ) * 100
        
        matches.append({
            "user_id": match.id,
            "name": match.name,
            "age": match.age,
            "gender": match.gender,
            "city": match.city,
            "interests": match.interests,
            "compatibility_score": round(compatibility_score, 2)
        })
    
    matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return matches