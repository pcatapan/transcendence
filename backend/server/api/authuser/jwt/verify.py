import hashlib
import json
import hmac
import base64
import logging

logger = logging.getLogger(__name__)

# Controlla se la firma del JWT è corretta o meno
def verify_signature(encoded_header, encoded_payload, signature, secret):
    data = f"{encoded_header}.{encoded_payload}".encode('utf-8')

    expected_signature = hmac.new(secret.encode('utf-8'), data, hashlib.sha256)
    expected_signature = base64.urlsafe_b64encode(expected_signature.digest()).rstrip(b'=').decode('utf-8')

    return hmac.compare_digest(expected_signature.encode('utf-8'), signature.encode('utf-8'))

def verify(jwt, secret):
	# Divido il jwt in tre parti
    encoded_header, encoded_payload, signature = jwt.split('.')

    if verify_signature(encoded_header, encoded_payload, signature, secret):

		# Aggiungo padding per il base64 se necessario
        encoded_header += '=' * ((4 - len(encoded_header) % 4) % 4)
        encoded_payload += '=' * ((4 - len(encoded_payload) % 4) % 4)

		# decodifico da base64 
        header_bytes = base64.urlsafe_b64decode(encoded_header)
        payload_bytes = base64.urlsafe_b64decode(encoded_payload)

		# converto in UTF-8
        header_str = header_bytes.decode('utf-8')
        payload_str = payload_bytes.decode('utf-8')

		# converto in ogetti python
        header = json.loads(header_str)
        payload = json.loads(payload_str)

        return payload
    else:
        raise Exception('Invalid signature')
