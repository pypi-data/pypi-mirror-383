#HNTE Codec

An lightweight Python implementation of the HNTE container format:
compressed (Deflate) + optional AES-GCM encryption + CRC integrity.

##Features
• V1 (XOR + Deflate) and (AES-GCM + Deflate)
• Supports Latin-5 (ISO-8859-9) and UTF-8 encodings.
• Integrity-Checked and tamper-evident

##Install
```bash
pip install hnte-codec

---------------------------------------
Usage---

from hnte_codec import save_text, load_text
key = b"A"*32 #256-bit AES key
save_text("demo.hnte", "Hello World!", key=key)
print(load_text("demo.hnte", key=key))