# 🔒 SecureVault  
**PIN-Protected Encryption for Text & Files**  
✨ Built with Flask, React, Tailwind, and Backblaze B2  

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-%23ff69b4)](CONTRIBUTING.md)  
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)  
![React](https://img.shields.io/badge/React-18.0%2B-%2361DAFB)  

---

## 🖼️ Screenshots  

- Home
![Home](https://github.com/user-attachments/assets/6694cb47-e48e-45b0-80f3-7fcacc6efb10)
- Encrypt
![Encrypt](https://github.com/user-attachments/assets/7184c48c-cdc7-419c-9b82-c36b4e32f8e5)
- Decrypt 
![Decrypt](https://github.com/user-attachments/assets/89b1feef-7d24-49ef-a162-f41c3f548428)

---


## 🚀 Features  
- 🔐 **SHA-256 PIN Hashing** + AES-256 Data Encryption  
- ☁️ Hybrid Storage:  
  - Text stored in MySQL (encrypted)  
  - Files on Backblaze B2 (encrypted filenames)  
- ⏳ Auto-Expiry: Files deleted after 48 hours  
- 🔑 Unique Shareable Key System  

---

## ⚡ Quick Start  

### Backend (Flask)  
1. Install dependencies:  
   ```bash
   pip install -r requirements.txt

    Start server:
    bash
    Copy

    flask run  # or python3 app.py

Frontend (React)

    Install packages:
    bash
    Copy

    npm install

    Start dev server:
    bash
    Copy

    npm run dev

🔧 How It Works

    Encrypt:

        User provides text/file + PIN

        Data encrypted → Stored in DB/Backblaze

        Returns unique key

    Decrypt:

        User provides key + PIN

        Validates PIN hash → Decrypts data

        Files become downloadable links

🛡️ Security

    PINs hashed with hashlib.sha256

    AES-256 encryption for data/files

    Keys expire after 48 hours

🌟 Future Plans

    🔑 User authentication system

    ⏰ Customizable expiry times (beyond 48hrs)

    📁 Batch file uploads

👥 Collaborators
@Cmutembei 
John Doe	Jane Smith	Alex Brown
❓ FAQ

Q: How long does my data stay?
A: 48 hours – we prioritize your privacy!

Q: File size limits?
A: Currently 100MB due to Backblaze B2 restrictions.
📜 License

Distributed under MIT License. See LICENSE for details.
