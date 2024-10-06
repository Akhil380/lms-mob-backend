
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional, Union

# JWT Settings
SECRET_KEY = "lmsSecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic model for token data
class TokenData(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    mobile: Optional[str] = None
    user_id: Union[int, str]

oauth2_scheme = HTTPBearer()

def create_access_token(data: dict):
    """
    Creates a JWT access token with a specified expiration time and user data.

    :param data: A dictionary containing user data like email, name, and mobile.
    :return: A JWT token as a string.
    """
    to_encode = data.copy()

    # expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # to_encode.update({"exp": expire})  # Add expiration time to the payload

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        email: str = payload.get("user_mail")
        name: str = payload.get("name")
        mobile: str = payload.get("mob")

        if user_id is None or email is None or name is None or mobile is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, email=email, name=name, mobile=mobile)

    except JWTError:
        raise credentials_exception

    return token_data


