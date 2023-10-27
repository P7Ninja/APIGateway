from jose import JWTError, jwt
from datetime import timedelta, datetime
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import dotenv_values
from typing import Annotated
import bcrypt

SALT = bcrypt.gensalt()
EXPIRES = 10

user_db: list[dict] = []

cfg = dotenv_values(".env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def user_exists(username: str):
    return any(u["username"] == username for u in user_db)

def db_get_user(username: str):
    return next((u for u in user_db if u['username'] == username), None)

def hash_pass(password: str):
    return bcrypt.hashpw(
        password.encode(),
        SALT
        )

def auth_user(db: list[dict], user: str, _pass: str):
    db_user = db_get_user(user)
    if db_user is None:
        print("here")
        return False
    return bcrypt.checkpw(_pass.encode(), db_user["password"])

def create_access_token(token_data: dict, expires_delta: timedelta):
    to_encode = {**token_data.copy(),**{"exp": datetime.utcnow() + expires_delta}}
    return jwt.encode(to_encode, cfg["JWT_SECRET"], cfg["JWT_ALG"])

def validate_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cfg["JWT_SECRET"], algorithms=[cfg["JWT_ALG"]])
        username: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    
    if username is None or not user_exists(username):
        raise credentials_exception
    return db_get_user(username)



@app.post("/token")
def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not auth_user(user_db, form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token({"sub": form_data.username}, timedelta(seconds=EXPIRES))
    return {"access_token": token, "token_type": "bearer"}

@app.post("/user")
def create_user(user: dict):
    if user_exists(user["username"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username!")
    user["password"] = hash_pass(user["password"])
    user["page"] = user["username"] + " secret page"
    user_db.append(user)
    return {"detail": "ok"}

@app.get("/user")
def get_user(user: Annotated[dict, Depends(validate_access_token)]):
    return f"<h1>{user['page']}</h1>"
