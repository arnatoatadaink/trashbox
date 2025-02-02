from datetime import datetime, timedelta
from typing import Union,Callable,List,Optional

from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pydantic_models import User
# from fastapi import 


import os

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = ""+os.environ["sec1"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secretsalt = ''+os.environ["sec2"]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None
    
async def get_host(Request: Request):
    return Request.client.host
    
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(
        data: dict,
        expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def make_userauth(get_user:Callable[[str],dict]):

    def authenticate_user(username: str, password: str):
        user = get_user(username)
        if not user:
            return False
        # user = UserInDB(**user.__dict__)
        if not verify_password(
                password+user.salt+secretsalt,
                user.hashedpassword):
            return False
        return user

    async def get_current_user(
            token: str = Depends(oauth2_scheme),
            host:str = Depends(get_host)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, SECRET_KEY,
                algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            last_logined: str = payload.get("last_logined")
            if last_logined != host:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = get_user(name=token_data.username)
        if user is None:
            raise credentials_exception
        return user


    async def get_current_active_user(
            current_user: User = Depends(
                get_current_user)):
        if current_user.disabled:
            raise HTTPException(
                status_code=400, detail="Inactive user")
        return current_user


    # @app.post("/token", response_model=Token)
    def login_for_access_token(
            form_data: OAuth2PasswordRequestForm = Depends(),
            host:str = Depends(get_host)):
        print("login_for_access_token",form_data)
        user = authenticate_user(
            form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        data = {
            "sub": user.name,
            "last_logined":host
        }
        access_token_expires = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=data, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}


    # @app.get("/users/me/", response_model=User)
    def read_users_me(
            current_user: \
                User = Depends(
                    get_current_active_user)):
        return current_user


    # @app.get("/users/me/items/")
    def read_own_items(
            current_user: User = Depends(
                get_current_active_user)):
        return [{"item_id": "Foo", "owner": current_user.username}]
    
    
    return {
        "get_current_active_user":get_current_active_user,
        "login_for_access_token" :login_for_access_token,
        "get_current_user"       :get_current_user,
        "read_users_me"          :read_users_me,
        "read_own_items"         :read_own_items
    }