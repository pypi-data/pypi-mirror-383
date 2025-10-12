import json
import base64

event_arns = ["arn:*"]


def reduce_event_source(event: dict) -> str:
    mapping: dict = event.get("mapping")
    fields = []
    for key, val in mapping.items():
        if isinstance(val, dict):
            val = json.dumps(val)
        # Fix: string val can't contains "'"
        fields.append("{}='{}'".format(key, val))
    return "Endpoints={"+",".join(fields)+"}"


def reduce_url_cors(cors: dict) -> str:
    fields = []
    for key, val in cors.items():
        key = key[0].upper() + key[1:]
        fields.append("{}={}".format(key, val))
    return ",".join(fields)


def encode_base64(text):
    encoded = base64.b64encode(text.encode('utf-8'))
    return encoded.decode('utf-8')


def decode_base64(encoded_text):
    decoded = base64.b64decode(encoded_text)
    return decoded.decode('utf-8')
