import base64
import secrets
import time
from typing import Dict

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from jose import jwt

from core.config import settings

router = APIRouter(prefix="/dev-oidc", tags=["dev-oidc"])

# Simple in-memory storage for authorization codes
_codes: Dict[str, Dict] = {}

# Generate an RSA keypair for signing ID tokens
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()

_kid = secrets.token_urlsafe(8)

_private_pem = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

_public_pem = _public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

def _base64url_no_pad(b: bytes) -> str:
    s = base64.urlsafe_b64encode(b).decode("utf-8")
    return s.rstrip("=")

def _pub_jwk():
    nums = _public_key.public_numbers()
    n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
    e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
    return {
        "kty": "RSA",
        "kid": _kid,
        "use": "sig",
        "alg": "RS256",
        "n": _base64url_no_pad(n),
        "e": _base64url_no_pad(e),
    }


@router.get("/.well-known/openid-configuration")
def openid_config(request: Request):
    issuer = str(request.base_url).rstrip("/")
    return {
        "issuer": issuer,
        "authorization_endpoint": f"{issuer}/authorize",
        "token_endpoint": f"{issuer}/token",
        "jwks_uri": f"{issuer}/.well-known/jwks.json",
    }


@router.get("/.well-known/jwks.json")
def well_known_jwks():
    return jwks()


@router.get("/authorize")
def authorize(
    request: Request,
    client_id: str,
    response_type: str = "code",
    scope: str = "openid",
    redirect_uri: str | None = None,
    state: str | None = None,
    nonce: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
):
    """Simulate an authorization endpoint that immediately issues a code and redirects back.

    This is for local development only.
    """
    # Create a code and persist minimal info
    code = secrets.token_urlsafe(24)
    _codes[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "nonce": nonce,
        "created_at": int(time.time()),
        "code_challenge": code_challenge,
    }

    # Build redirect
    if not redirect_uri:
        return JSONResponse({"error": "missing_redirect_uri"}, status_code=400)

    sep = "?" if "?" not in redirect_uri else "&"
    redirect_to = f"{redirect_uri}{sep}code={code}"
    if state:
        redirect_to += f"&state={state}"

    return RedirectResponse(url=redirect_to)


@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(None),
    redirect_uri: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None),
    code_verifier: str = Form(None),
):
    """Simulate token exchange. Returns an id_token signed with RS256 using the generated key."""
    if grant_type != "authorization_code":
        return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)

    if not code or code not in _codes:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    entry = _codes.pop(code)

    # Basic validation of client_id and redirect_uri
    if client_id and client_id != entry.get("client_id"):
        return JSONResponse({"error": "invalid_client"}, status_code=400)
    if redirect_uri and redirect_uri != entry.get("redirect_uri"):
        return JSONResponse({"error": "invalid_request", "error_description": "redirect_uri mismatch"}, status_code=400)

    now = int(time.time())
    issuer = settings.oidc_issuer_url or f"http://localhost:8000/dev-oidc"
    id_claims = {
        "iss": issuer,
        "aud": client_id or entry.get("client_id"),
        "sub": "dev-user-1",
        "iat": now,
        "exp": now + 600,
    }
    if entry.get("nonce"):
        id_claims["nonce"] = entry.get("nonce")

    # Sign ID token with RS256
    id_token = jwt.encode(id_claims, _private_pem, algorithm="RS256", headers={"kid": _kid})

    return {
        "access_token": "dev-access-token",
        "id_token": id_token,
        "token_type": "Bearer",
        "expires_in": 600,
    }


@router.get("/jwks.json")
def jwks():
    return {"keys": [_pub_jwk()]}
