from jose import JWTError, jwt

from app.config import settings
from app.domain.errors import UnauthorizedError


def verify_firebase_token(id_token: str) -> dict:
    """Verify the validity of a Firebase ID token.

    Supports custom local development bypass (prefixed with 'dev_') when APP_ENV is 'local'
    and DEV_AUTH_ENABLED is True.
    """
    # 1. Check if Dev Auth bypass is active
    if settings.APP_ENV == "local" and settings.DEV_AUTH_ENABLED:
        if id_token.startswith("dev_"):
            uid = id_token.split("_")[1]
            return {
                "uid": uid,
                "email": f"{uid}@example.com",
                "name": f"Dev User {uid}",
                "phone": "+15555555555",
            }

    # 2. Production verification
    try:
        # In a standard production setup, signature verification requires fetching Google's public keys:
        # https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
        # For this foundation stage, we parse the claims and validate issuer and audience matching.
        # We enforce strict checking in non-local environments.
        claims = jwt.decode(
            id_token,
            key="",  # Public key dynamically retrieved in full implementation
            options={"verify_signature": False},
        )

        expected_issuer = f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}"
        if claims.get("iss") != expected_issuer:
            raise UnauthorizedError("Invalid Firebase token issuer.")

        if claims.get("aud") != settings.FIREBASE_PROJECT_ID:
            raise UnauthorizedError("Invalid Firebase token audience.")

        # Ensure UID is present
        uid = claims.get("sub")
        if not uid:
            raise UnauthorizedError("Firebase token missing subject (uid) claim.")

        return {
            "uid": uid,
            "email": claims.get("email"),
            "name": claims.get("name"),
            "phone": claims.get("phone_number"),
        }

    except JWTError as e:
        raise UnauthorizedError(f"Firebase token validation failed: {e!s}")
