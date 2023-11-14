from datetime import timedelta, datetime
from jose import jwt, JWTError


class JWTEncoder:
    def __init__(self, cfg: dict) -> None:
        self.__cfg = cfg


    def encode(self, username: str, id: int, expires_delta: timedelta):
        return jwt.encode({
            "sub": username, 
            "id": id,
            "exp": datetime.utcnow() + expires_delta
            }, self.__cfg["JWT_SECRET"], self.__cfg["JWT_ALG"])

    def decode_token(self, token: str) -> dict |None:
        try:
            payload = jwt.decode(token, self.__cfg["JWT_SECRET"], algorithms=[self.__cfg["JWT_ALG"]])
            if any(x not in payload for x in ["sub", "id", "exp"]):
                return None
            return payload
        except JWTError:
            return None
