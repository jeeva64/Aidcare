from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt=settings.SECRET_KEY)

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt=settings.SECRET_KEY, max_age=expiration)
        return email
    except Exception:
        return None
