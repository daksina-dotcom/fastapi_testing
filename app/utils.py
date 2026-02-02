import os
import jwt
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta,timezone

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(data: dict):
    encode_dict = data.copy()
    if "sub" in encode_dict:
        encode_dict["sub"] = str(encode_dict["sub"])
    start = datetime.now(timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    encode_dict.update({"exp": expire})
    return jwt.encode(encode_dict, secret_key, algorithm)


def decode_token(token: str):
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        print("Error: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Error: Invalid Token - {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None
