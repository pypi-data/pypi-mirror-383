import hashlib

def get_content_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode()).hexdigest()
