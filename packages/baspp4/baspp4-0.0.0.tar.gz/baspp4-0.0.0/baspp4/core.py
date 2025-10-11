try:
    import pybase64 as base64_impl
except ImportError:
    import base64 as base64_impl

def b64encode(data: bytes) -> bytes:
    """
    Encode bytes-like object using Base64.
    """
    return base64_impl.b64encode(data)

def b64decode(data: bytes) -> bytes:
    """
    Decode Base64 encoded bytes-like object.
    """
    return base64_impl.b64decode(data)

def urlsafe_b64encode(data: bytes) -> bytes:
    """
    Encode bytes-like object using URL-safe Base64.
    """
    return base64_impl.urlsafe_b64encode(data)

def urlsafe_b64decode(data: bytes) -> bytes:
    """
    Decode URL-safe Base64 encoded bytes-like object.
    """
    return base64_impl.urlsafe_b64decode(data)

