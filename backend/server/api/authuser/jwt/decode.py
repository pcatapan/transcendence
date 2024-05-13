import json
import base64

def base64_urlsafe_decode(data):
    padding_size = 4 - (len(data) % 4)
    if padding_size:
        data += '=' * padding_size
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except (ValueError, base64.binascii.Error) as e:
        raise ValueError("Invalid base64-encoded string.") from e

def decode(jwt):
    try:
        parts = jwt.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format.")
        
        encoded_header, encoded_payload, _ = parts
        header = json.loads(base64_urlsafe_decode(encoded_header))
        payload = json.loads(base64_urlsafe_decode(encoded_payload))
        
        return {
			'header': header,
			'payload': payload
		}
    except Exception as e:
        raise ValueError("Failed to decode JWT: {}".format(e)) from e

      