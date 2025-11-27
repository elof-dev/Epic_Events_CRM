from argon2 import PasswordHasher
import jwt
import datetime
from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_SECONDS


class AuthService:
    def __init__(self):
        self._ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self._ph.hash(password)

    def verify_password(self, hashed: str, password: str) -> bool:
        try:
            return self._ph.verify(hashed, password)
        except Exception:
            return False

    def create_token(self, user_id: int) -> str:
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {"sub": str(user_id), "iat": now, "exp": now + datetime.timedelta(seconds=JWT_EXP_SECONDS)}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    def decode_token(self, token: str):
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
