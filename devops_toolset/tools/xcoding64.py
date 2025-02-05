"""Tools for base64 encoding and decoding"""

import base64


def encode(text: str):
    """Encodes a string to base64 format

    Args:
        text: UTF-8 string to be encoded in base64 format
    """

    text_bytes = text.encode("utf-8")
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("utf-8")


def decode(base64_text):
    """Decodes a string from base64 format

    Args:
        base64_text: Base64 string to be decoded to UTF-8 format
    """

    base64_text_bytes = base64_text.encode("utf-8")
    text_bytes = base64.b64decode(base64_text_bytes)
    return text_bytes.decode("utf-8")


if __name__ == "__main__":
    help(__name__)
