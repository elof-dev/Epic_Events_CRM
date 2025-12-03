from argon2 import PasswordHasher
import jwt
import datetime
from app.db.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_SECONDS


class AuthService:
    """Service d'authentification minimal.

    Rôle : fournir des utilitaires pour le hachage et la vérification des
    mots de passe, ainsi que la création et le décodage de tokens JWT.

    Méthodes principales :
    - `hash_password(password: str) -> str` : retourne une chaîne contenant
        le mot de passe haché (utilise Argon2).
    - `verify_password(hashed: str, password: str) -> bool` : vérifie qu'un
        mot de passe en clair correspond au hachage ; retourne `True`/`False`.
    - `create_token(user_id: int) -> str` : génère et retourne un token JWT
        encodant l'`user_id` (champ `sub`) et les claims `iat`/`exp`.
    - `decode_token(token: str)` : décode et retourne le payload du token JWT.

    Remarques :
    - Les durées et la clé du JWT sont lues depuis la configuration (`app.config`).
    - `verify_password` capture les exceptions et renvoie `False` en cas d'erreur.
    """

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
