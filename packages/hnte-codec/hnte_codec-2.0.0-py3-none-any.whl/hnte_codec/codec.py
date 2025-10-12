# hnte_codec.py
# Python implementation of an HNTE-style container:
# v1: MAGIC "HNTE" | ver=1 | enc(1) | flags(1) | orig_len(4) | comp_len(4) | crc32(4) | payload
#     payload = XOR(deflate(text_bytes))
# v2: MAGIC "HNTE" | ver=2 | enc(1) | flags(1) | orig_len(4) | comp_len(4) | crc32(4) | [nonce_len(1) nonce][tag_len(1) tag] payload
#     payload = deflate(text_bytes) if not ENCRYPTED
#     if ENCRYPTED: payload = AESGCM.encrypt(nonce, deflated, aad=None)[:-16], tag=last16
#
# Notes:
# - enc: 1=Latin-5 (iso-8859-9), 2=UTF-8
# - flags: bit 0x01=XOR (kept for v1/back-compat), 0x02=COMPRESSED, 0x04=ENCRYPTED
# - CRC32 is computed over the stored payload (post-XOR, post-encrypt as applicable)


#Module cryptography and future required!
from __future__ import annotations
import struct, zlib, os, secrets
from typing import Optional

MAGIC = b"HNTE"
VER_V1 = 1
VER_V2 = 2

ENC_LATIN5 = 1   # ISO-8859-9
ENC_UTF8   = 2

FLAG_XOR        = 0x01
FLAG_COMPRESSED = 0x02
FLAG_ENCRYPTED  = 0x04

_XOR_KEY = 0xA7

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
except Exception:
    AESGCM = None  # encryption unavailable unless 'cryptography' is installed


def _to_bytes(text: str, prefer_latin5: bool) -> tuple[bytes, int]:
    """Encode text to bytes, trying ISO-8859-9 when requested."""
    if prefer_latin5:
        try:
            return text.encode("iso-8859-9"), ENC_LATIN5
        except UnicodeEncodeError:
            pass
    return text.encode("utf-8"), ENC_UTF8


def _from_bytes(buf: bytes, enc_id: int) -> str:
    if enc_id == ENC_LATIN5:
        return buf.decode("iso-8859-9")
    return buf.decode("utf-8")


def _xor_in_place(b: bytearray) -> None:
    for i in range(len(b)):
        b[i] ^= _XOR_KEY


def save_text(
    path: str,
    text: str,
    key: Optional[bytes] = None,
    *,
    version: int = VER_V2,
    prefer_latin5: bool = False,
    force_xor_v2: bool = False,
    compress_level: int = 9,
) -> None:
    """
    Save text into an HNTE container.
    - version: 1 (legacy XOR+deflate) or 2 (recommended; deflate + optional AES-GCM)
    - key: 16/24/32 bytes for AES-GCM; if None => no encryption
    - prefer_latin5: try ISO-8859-9 first (good for Turkish), fallback to UTF-8
    - force_xor_v2: if True, set XOR flag on v2 (kept for rare C# compatibility needs)
    """
    if text is None:
        text = ""
    raw, enc_id = _to_bytes(text, prefer_latin5)
    comp = zlib.compress(raw, level=compress_level)

    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(MAGIC)

        if version == VER_V1:
            # v1: XOR + deflate, always compressed + XOR, never encrypted
            ver = VER_V1
            flags = FLAG_COMPRESSED | FLAG_XOR
            comp_to_store = bytearray(comp)
            _xor_in_place(comp_to_store)
            crc = zlib.crc32(comp_to_store) & 0xFFFFFFFF
            f.write(struct.pack("<B", ver))
            f.write(struct.pack("<B", enc_id))
            f.write(struct.pack("<B", flags))
            f.write(struct.pack("<I", len(raw)))
            f.write(struct.pack("<I", len(comp_to_store)))
            f.write(struct.pack("<I", crc))
            f.write(comp_to_store)
        elif version == VER_V2:
            ver = VER_V2
            flags = FLAG_COMPRESSED
            xor_flag = FLAG_XOR if force_xor_v2 else 0

            if key:
                if AESGCM is None:
                    raise RuntimeError("cryptography not installed; cannot encrypt")
                flags |= FLAG_ENCRYPTED
                # AES-GCM over deflated content
                aes = AESGCM(key)
                nonce = secrets.token_bytes(12)
                ct = aes.encrypt(nonce, comp, None)  # ct = ciphertext + tag(16)
                tag = ct[-16:]
                payload = ct[:-16]
                if xor_flag:
                    buf = bytearray(payload); _xor_in_place(buf); payload = bytes(buf)
                comp_len = len(payload)
                crc = zlib.crc32(payload) & 0xFFFFFFFF

                f.write(struct.pack("<B", ver))
                f.write(struct.pack("<B", enc_id))
                f.write(struct.pack("<B", flags | xor_flag))
                f.write(struct.pack("<I", len(raw)))
                f.write(struct.pack("<I", comp_len))
                f.write(struct.pack("<I", crc))
                f.write(struct.pack("<B", len(nonce))); f.write(nonce)
                f.write(struct.pack("<B", len(tag)));   f.write(tag)
                f.write(payload)
            else:
                # not encrypted
                payload = comp
                if xor_flag:
                    buf = bytearray(payload); _xor_in_place(buf); payload = bytes(buf)
                comp_len = len(payload)
                crc = zlib.crc32(payload) & 0xFFFFFFFF

                f.write(struct.pack("<B", ver))
                f.write(struct.pack("<B", enc_id))
                f.write(struct.pack("<B", flags | xor_flag))
                f.write(struct.pack("<I", len(raw)))
                f.write(struct.pack("<I", comp_len))
                f.write(struct.pack("<I", crc))
                f.write(payload)
        else:
            raise ValueError("Unsupported HNTE version; use 1 or 2")

    # atomic replace
    if os.path.exists(path):
        os.replace(tmp, path)
    else:
        os.rename(tmp, path)


def load_text(path: str, key: Optional[bytes] = None) -> str:
    """Load text from an HNTE container. Provide key for AES-GCM files."""
    with open(path, "rb") as f:
        if f.read(4) != MAGIC:
            raise ValueError("Not an HNTE file")
        ver = struct.unpack("<B", f.read(1))[0]

        if ver == VER_V1:
            enc_id = struct.unpack("<B", f.read(1))[0]
            flags  = struct.unpack("<B", f.read(1))[0]
            orig_len = struct.unpack("<I", f.read(4))[0]
            comp_len = struct.unpack("<I", f.read(4))[0]
            stored_crc = struct.unpack("<I", f.read(4))[0]
            payload = bytearray(f.read(comp_len))
            if (zlib.crc32(payload) & 0xFFFFFFFF) != stored_crc:
                raise ValueError("CRC mismatch (v1)")
            # v1 payload was XOR(deflate(raw))
            if (flags & FLAG_XOR) == 0:
                # Some older variants might omit flag; tolerate if needed:
                pass
            _xor_in_place(payload)
            raw = zlib.decompress(bytes(payload))
            if len(raw) != orig_len:  # len check optional
                pass
            return _from_bytes(raw, enc_id)

        elif ver == VER_V2:
            enc_id = struct.unpack("<B", f.read(1))[0]
            flags  = struct.unpack("<B", f.read(1))[0]
            orig_len = struct.unpack("<I", f.read(4))[0]
            comp_len = struct.unpack("<I", f.read(4))[0]
            stored_crc = struct.unpack("<I", f.read(4))[0]

            encrypted = (flags & FLAG_ENCRYPTED) != 0
            xor_flag  = (flags & FLAG_XOR) != 0

            if encrypted:
                nonce_len = struct.unpack("<B", f.read(1))[0]
                nonce = f.read(nonce_len)
                tag_len = struct.unpack("<B", f.read(1))[0]
                tag = f.read(tag_len)
                payload = f.read(comp_len)
                if (zlib.crc32(payload) & 0xFFFFFFFF) != stored_crc:
                    raise ValueError("CRC mismatch (v2/encrypted)")
                if not key:
                    raise ValueError("AES key required to open this file")
                if AESGCM is None:
                    raise RuntimeError("cryptography not installed; cannot decrypt")
                aes = AESGCM(key)
                ct = payload + tag
                comp = aes.decrypt(nonce, ct, None)
                if xor_flag:
                    buf = bytearray(comp); _xor_in_place(buf); comp = bytes(buf)
                raw = zlib.decompress(comp)
                if len(raw) != orig_len:
                    pass
                return _from_bytes(raw, enc_id)
            else:
                payload = f.read(comp_len)
                if (zlib.crc32(payload) & 0xFFFFFFFF) != stored_crc:
                    raise ValueError("CRC mismatch (v2)")
                if xor_flag:
                    buf = bytearray(payload); _xor_in_place(buf); payload = bytes(buf)
                raw = zlib.decompress(payload)
                if len(raw) != orig_len:
                    pass
                return _from_bytes(raw, enc_id)

        else:
            raise ValueError(f"Unsupported HNTE version: {ver}")