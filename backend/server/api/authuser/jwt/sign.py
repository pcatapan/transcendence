import base64
import hashlib
import hmac
import json

def base64_urlsafe_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

#Create the JWT signature
def create_signature(encoded_header, encoded_payload, secret):
    data = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    
    # Crea l'oggetto HMAC direttamente
    h = hmac.new(secret.encode('utf-8'), data, hashlib.sha256)

    # Calcola il digest e codificalo in base64 URL-safe
    return base64_urlsafe_encode(h.digest())

#Create a signed JWT from the payload and secret
def sign(payload, secret):
    if not secret:
        raise ValueError("Secret cannot be empty")

    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = base64_urlsafe_encode(json.dumps(header).encode('utf-8'))
    encoded_payload = base64_urlsafe_encode(json.dumps(payload).encode('utf-8'))

    signature = create_signature(encoded_header, encoded_payload, secret)

    return f"{encoded_header}.{encoded_payload}.{signature}"
