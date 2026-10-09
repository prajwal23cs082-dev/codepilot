from fastapi import FastAPI, Depends, HTTPException
from typing import List

from .models import User, UserCreate

app = FastAPI(title="Demo FastAPI Project")

# In-memory database for demo
users_db = []
user_id_counter = 1

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    global user_id_counter
    # Intentional bug for the agent to fix: missing validation
    new_user = User(id=user_id_counter, username=user.username, email=user.email)
    users_db.append(new_user)
    user_id_counter += 1
    return new_user

@app.get("/users", response_model=List[User])
def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for u in users_db:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")

# TODO: Add JWT authentication so only authenticated users can get the list of users
