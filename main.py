from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Security configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory database
fake_db = {}

# Pydantic models
class Payload(BaseModel):
    numbers: List[int]

class BinarySearchPayload(BaseModel):
    numbers: List[int]
    target: int

class UserCredentials(BaseModel):
    username: str
    password: str

# Authentication functions
def create_token(username: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(
        {"sub": username, "exp": expiration},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# Modifica la función verify_token para usar las excepciones correctas
def verify_token(token: str = Query(...)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except Exception:  # Usamos una excepción general en lugar de jwt.JWTError
        raise HTTPException(status_code=401, detail="Could not validate token")
# Endpoints
@app.post("/register")
async def register(credentials: UserCredentials):
    if credentials.username in fake_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = pwd_context.hash(credentials.password)
    fake_db[credentials.username] = hashed_password
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(credentials: UserCredentials):
    if credentials.username not in fake_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not pwd_context.verify(credentials.password, fake_db[credentials.username]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(credentials.username)
    return {"access_token": token}

@app.post("/bubble-sort")
async def bubble_sort(payload: Payload, username: str = Depends(verify_token)):
    numbers = payload.numbers.copy()
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return {"numbers": numbers}
@app.post("/filter-even")
async def filter_even(payload: Payload, username: str = Depends(verify_token)):
    even_numbers = [num for num in payload.numbers if num % 2 == 0]
    return {"even_numbers": even_numbers}

@app.post("/sum-elements")
async def sum_elements(payload: Payload, username: str = Depends(verify_token)):
    return {"sum": sum(payload.numbers)}

@app.post("/max-value")
async def max_value(payload: Payload, username: str = Depends(verify_token)):
    return {"max": max(payload.numbers)}

@app.post("/binary-search")
async def binary_search(payload: BinarySearchPayload, username: str = Depends(verify_token)):
    numbers = sorted(payload.numbers)
    left, right = 0, len(numbers) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == payload.target:
            return {"found": True, "index": mid}
        elif numbers[mid] < payload.target:
            left = mid + 1
        else:
            right = mid - 1
            
    return {"found": False, "index": -1}