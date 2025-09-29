import hashlib
import base64

def generate_hash_512_HEXDIGEST(content:str):
    return hashlib.sha512(content.encode()).hexdigest()

def encode_base_64(content:str):
    return base64.b64encode(content.encode()).decode()

def decode_base_64(content:str):
    return base64.b64encode(content).decode()