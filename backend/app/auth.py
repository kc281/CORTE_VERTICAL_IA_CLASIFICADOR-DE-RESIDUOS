import os
import json
from functools import lru_cache

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
security = HTTPBearer()

@lru_cache(maxsize=1)
def _get_jwks() -> list[dict]:
    """Obtiene y cachea las llaves públicas (JWKS) de Supabase."""
    url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["keys"]

def _get_public_key(kid: str | None) -> object:
    """Devuelve la llave pública que coincide con el 'kid' del token."""
    keys = _get_jwks()
    if kid:
        matched = [k for k in keys if k.get("kid") == kid]
        key_data = matched[0] if matched else keys[0]
    else:
        key_data = keys[0]
    return jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_data))

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        public_key = _get_public_key(kid)

       
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_aud": True}
        )
        return {"user_id": payload.get("sub"), "email": payload.get("email")}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError as e:
        print(f" ERROR AUTH DETALLADO: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except Exception as e:
        print(f" ERROR CRÍTICO AUTH: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno de autenticación")