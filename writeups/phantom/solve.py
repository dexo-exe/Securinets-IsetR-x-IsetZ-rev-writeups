#!/usr/bin/env python3
"""
Securinets CTF – "Phantom"  ·  SOLUTION  (organiser only)
══════════════════════════════════════════════════════════

INTENDED SOLVE PATH:
  1. strings/Ghidra → only blob arrays, nothing readable
  2. Run binary → exits silently (anti-debug fires)
  3. Open in Ghidra → find the 4 ad_* functions, each ends with _exit(1)
  4. Patch each conditional jump before _exit → NOP (90 90) or flip to JMP
  5. Load patched binary in GDB
  6. Break on deobf or AES_set_decrypt_key → dump key[16] from memory
  7. Also dump iv[16] from memory after second deobf call
  8. Extract CT_OBF from binary data section (48 bytes)
  9. Reconstruct and decrypt here

WHAT YOU RECOVER FROM GDB:
  After breaking on AES_set_decrypt_key, first arg (RDI) points to the key:
    (gdb) break AES_set_decrypt_key
    (gdb) run
    (gdb) x/16bx $rdi
    → 5e c0 1c a1 31 41 59 26 53 58 97 93 23 84 62 64

  OR break right after the deobf() call for the key:
    (gdb) break *deobf+<ret_offset>
    (gdb) x/16bx <key_addr>
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ── What you extract from GDB (key and IV dumped from stack) ─────────────────
# These are the RAW (de-obfuscated) values visible in the debugger
AES_KEY = bytes.fromhex("5ec01ca1314159265358979323846264")
IV      = bytes.fromhex("fedcba98765432100f1e2d3c4b5a6978")

# ── What you extract statically (CT_OBF is still readable in Ghidra) ─────────
# Still obfuscated — you ALSO need the deobf formula from the binary
# Formula: out[i] = in[i] ^ (((i * 0x37) ^ 0xA5) & 0xFF)
CT_OBF = bytes([
    0xFD, 0x2A, 0xE5, 0xC4, 0x14, 0x76, 0x6E, 0x52,
    0x38, 0xF4, 0xB4, 0xBA, 0x0D, 0xAA, 0x89, 0x63,
    0x68, 0xDB, 0x32, 0x6D, 0xB1, 0x55, 0x8A, 0x2D,
    0x03, 0x69, 0x6D, 0xCA, 0x6E, 0x70, 0xCD, 0xA4,
    0xFC, 0x09, 0xB3, 0x73, 0x89, 0xE3, 0x10, 0x96,
    0xE2, 0x46, 0x3F, 0x57, 0x1D, 0x46, 0xF4, 0x2D
])

# ── De-obfuscate CT using the formula reversed from the deobf() loop ─────────
CT = bytes(b ^ (((i * 0x37) ^ 0xA5) & 0xFF) for i, b in enumerate(CT_OBF))
print(f"CT  (raw) = {CT.hex()}")
print(f"KEY (GDB) = {AES_KEY.hex()}")
print(f"IV  (GDB) = {IV.hex()}")

# ── AES-128-CBC decrypt ───────────────────────────────────────────────────────
flag = unpad(AES.new(AES_KEY, AES.MODE_CBC, IV).decrypt(CT), 16).decode()
print(f"\nFLAG → {flag}")