from app.core.config import settings


# ImageKit configuration (will be used when frontend uploads directly)
def get_imagekit_auth_params():
    """
    Returns ImageKit auth params for client-side upload.
    In production, you'd generate signature here.
    """
    return {
        "publicKey": settings.IMAGEKIT_PUBLIC_KEY,
        "urlEndpoint": settings.IMAGEKIT_URL_ENDPOINT,
    }
