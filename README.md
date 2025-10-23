# FLUX-Vanity-Address-Generator
# 🪙 FLUX Vanity Address Generator (CPU-only)  A lightweight **multi-core vanity address generator** for **FLUX** (`t1` and `t3` addresses).   It runs **entirely on CPU**, requires no GPU or CUDA, and works out of the box on Windows, Linux, and macOS.
---

## 🚀 Features

✅ Multi-core CPU processing (uses all available cores)  
✅ Choose between:
- **Zelcore (t1)** or **SSP (t3)** address types  
✅ Custom character pattern (default: `FLUX`)  
✅ Option to search:
- Pattern **anywhere** in the address, or  
- Only **after the t# prefix**  
✅ Case-sensitive or case-insensitive matching  
✅ Automatically saves results to `found_addresses.txt`  

---

## 🧩 Requirements

You need Python 3.9 or newer.

### 🔧 Install Python (Windows)
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download and install Python (check **"Add Python to PATH"** during installation)
3. Open **PowerShell** and verify installation:

python --version
You should see something like:
Python 3.12.0

📦 Install Required Packages
Run the following in PowerShell (or your terminal):
pip install ecdsa

That’s it — no GPU, no CUDA, no special dependencies.

💻 How to Run
Download or clone this repository:

git clone https://github.com/<yourusername>/flux-vanity-cpu.git
cd flux-vanity-cpu

Run the script:

python flux_vanity_cpu.py

Follow the on-screen prompts:

Choose address type (1 = Zelcore [t1], 2 = SSP [t3]):
Enter desired characters (default: FLUX):
Should the pattern be (1) after t# or (2) anywhere in the address?
Should the pattern be case sensitive? (y/n, default n):
The generator will start working using all CPU cores.
You’ll see progress updates every few seconds:

Tried 1,500,000 keys — 300,000 keys/s — elapsed 5s
When a match is found:

=== MATCH FOUND ===
Worker: 3
Address: t3FLUX9JkLd3hRbJQwLkzjWL5v2PQGNaLw
Private key (hex): 4a83f7d84d0e981c4e567de9e8994df29...
Tried: 7,210,000 keys in 24s
✅ Result saved to: found_addresses.txt

📁 Output File

All found addresses are saved in the same directory as the script:

found_addresses.txt

Each entry includes:

[2025-10-23 12:44:15]
Type: SSP (t3)
Address: t3FLUX9JkLd3hRbJQwLkzjWL5v2PQGNaLw
Private key (hex): 4a83f7d84d0e981c4e567de9e8994df29...
Pattern: FLUX
Position: after t#
Case-sensitive: No
Keys tested: 7,210,000

⚙️ Tips

Searching for longer or more specific patterns takes exponentially longer.
Example: finding “FLUX” is easy — “FLUXX” can take 100× longer.

You can safely stop the script anytime with Ctrl + C.

The progress monitor updates every 5 seconds.

🧠 How It Works (Simplified)

The script generates random ECDSA secp256k1 private keys.

Each key’s corresponding public key is hashed using SHA-256 → RIPEMD-160 (hash160).

A redeem script is built and hashed again to form the P2SH/P2PKH address.

The resulting address is checked against your chosen pattern.

If it matches, the private key and address are saved.

🛑 Security Notice

Never share your private key.

This generator runs locally — no data is sent anywhere.


🧾 License

MIT License © 2025
Feel free to fork, modify, and share — just credit the original repository.
