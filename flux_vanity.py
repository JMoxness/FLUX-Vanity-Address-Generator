#!/usr/bin/env python3
"""
FLUX Vanity Address Generator (CPU-only)
Author: ChatGPT Assistant
"""

import time
import hashlib
import secrets
import os
from multiprocessing import Process, Queue, Value, cpu_count
from ecdsa import SigningKey, SECP256k1
from threading import Thread

# ----------------- FLUX constants -----------------
ZELCORE_P2PKH_VERSION = b"\x1c\xb8"  # t1
SSP_P2SH_VERSION      = b"\x1c\xbd"  # t3
BASE58_ALPHABET       = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# ----------------- Hashing helpers -----------------
def sha256(b): return hashlib.sha256(b).digest()
def ripemd160(b): h = hashlib.new("ripemd160"); h.update(b); return h.digest()
def hash160(b): return ripemd160(sha256(b))

def base58check_encode(payload):
    checksum = sha256(sha256(payload))[:4]
    data = payload + checksum
    x = int.from_bytes(data, "big")
    n_pad = len(data) - len(data.lstrip(b"\x00"))
    b58 = bytearray()
    while x > 0:
        x, r = divmod(x, 58)
        b58.append(BASE58_ALPHABET[r])
    b58 = (BASE58_ALPHABET[0:1] * n_pad) + bytes(reversed(b58))
    return b58.decode()

def compress_pubkey(pub):
    x = pub[1:33]
    y = pub[33:65]
    prefix = b"\x03" if (y[-1] & 1) else b"\x02"
    return prefix + x

def make_redeemscript(pubhash20):
    return b"\x76\xa9\x14" + pubhash20 + b"\x88\xac"

def address_from_script_hash(script_hash, version_bytes):
    return base58check_encode(version_bytes + script_hash)

def generate_keypair():
    priv = secrets.token_bytes(32)
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub = b"\x04" + vk.to_string()
    compressed = compress_pubkey(pub)
    pubhash = hash160(compressed)
    redeem = make_redeemscript(pubhash)
    script_hash = hash160(redeem)
    return priv.hex(), script_hash

# ----------------- Worker -----------------
def worker_cpu(pattern, q, counter, stop_flag, worker_id,
               version_bytes, anywhere, case_sensitive, batch=1000):
    pat_len = len(pattern)
    while not stop_flag.value:
        for _ in range(batch):
            priv_hex, script_hash = generate_keypair()
            addr = address_from_script_hash(script_hash, version_bytes)
            if anywhere:
                match = pattern in addr if case_sensitive else pattern.lower() in addr.lower()
            else:
                seg = addr[2:2+pat_len]
                match = seg == pattern if case_sensitive else seg.lower() == pattern.lower()
            if match:
                q.put({"found": True, "priv_hex": priv_hex, "address": addr, "worker": worker_id})
                stop_flag.value = 1
                return
        with counter.get_lock():
            counter.value += batch

# ----------------- Progress monitor -----------------
def monitor(counter, start_time, stop_flag):
    last = 0
    while not stop_flag.value:
        time.sleep(5)
        with counter.get_lock():
            total = counter.value
        rate = (total - last) / 5
        last = total
        elapsed = time.time() - start_time
        print(f"Tried {total:,} keys — {rate:,.0f} keys/s — elapsed {int(elapsed)}s")

# ----------------- Main -----------------
def main():
    print("=== FLUX Vanity Address Generator (CPU-only) ===\n")

    # Address type
    while True:
        addr_type = input("Choose address type (1 = Zelcore [t1], 2 = SSP [t3]): ").strip()
        if addr_type in ["1", "2"]:
            break
        print("Invalid choice. Enter 1 or 2.")
    version_bytes = ZELCORE_P2PKH_VERSION if addr_type == "1" else SSP_P2SH_VERSION
    prefix_start = "t1" if addr_type == "1" else "t3"

    # Pattern
    pattern = input("Enter desired characters (default: FLUX): ").strip()
    if not pattern:
        pattern = "FLUX"

    # Position
    pos_choice = input("Should the pattern be (1) after t# or (2) anywhere in the address? ").strip()
    anywhere = True if pos_choice == "2" else False

    # Case sensitivity
    case_choice = input("Should the pattern be case sensitive? (y/n, default n): ").strip().lower()
    case_sensitive = True if case_choice == "y" else False

    # CPU workers
    workers = max(1, cpu_count() - 1)
    print(f"\nStarting search for {prefix_start}{pattern} "
          f"({'anywhere' if anywhere else 'after t#'}, "
          f"{'case-sensitive' if case_sensitive else 'case-insensitive'}) "
          f"with {workers} workers...\n")

    q = Queue()
    counter = Value("Q", 0)
    stop_flag = Value("b", 0)
    start = time.time()

    Thread(target=monitor, args=(counter, start, stop_flag), daemon=True).start()

    procs = []
    for i in range(workers):
        p = Process(target=worker_cpu,
                    args=(pattern, q, counter, stop_flag, i,
                          version_bytes, anywhere, case_sensitive))
        p.start()
        procs.append(p)

    try:
        result = q.get()
    except KeyboardInterrupt:
        stop_flag.value = 1
        result = None
    elapsed = time.time() - start

    if result and result.get("found"):
        addr = result["address"]
        priv_hex = result["priv_hex"]
        print("\n=== MATCH FOUND ===")
        print(f"Worker: {result['worker']}")
        print(f"Address: {addr}")
        print(f"Private key (hex): {priv_hex}")
        print(f"Tried: {counter.value:,} keys in {int(elapsed)}s\n")

        # save
        out_path = os.path.join(os.getcwd(), "found_addresses.txt")
        with open(out_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"Type: {'Zelcore (t1)' if addr_type == '1' else 'SSP (t3)'}\n")
            f.write(f"Address: {addr}\n")
            f.write(f"Private key (hex): {priv_hex}\n")
            f.write(f"Pattern: {pattern}\n")
            f.write(f"Position: {'anywhere' if anywhere else 'after t#'}\n")
            f.write(f"Case-sensitive: {'Yes' if case_sensitive else 'No'}\n")
            f.write(f"Keys tested: {counter.value:,}\n\n")
        print(f"✅ Result saved to: {out_path}\n")
    else:
        print("No result found or interrupted.")

    stop_flag.value = 1
    for p in procs:
        p.terminate()
    for p in procs:
        p.join(timeout=1)

if __name__ == "__main__":
    main()