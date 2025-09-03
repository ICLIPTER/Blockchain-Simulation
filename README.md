# Mini Blockchain Simulation

A simple interactive blockchain simulation built with **Python (FastAPI)** for the backend and **React + TailwindCSS** for the frontend. This project demonstrates the fundamentals of blockchain, wallets, transactions, and mining in a fun, visual way.

---

## Features

- Create wallets with ECDSA key pairs.
- Check wallet balances.
- Send transactions between wallets.
- Mine new blocks and receive mining rewards.
- View the blockchain in real time.
- Fully interactive React dashboard with Tailwind 4 styling.

---

## Tech Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn, ECDSA
- **Frontend:** React, TailwindCSS 4
- **Communication:** REST API endpoints

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Blockchain-Simulation

python -m venv .venv
# Activate
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux

pip install fastapi uvicorn ecdsa
python -m uvicorn server:app --reload
http://localhost:8000

```
cd blockchain-ui
npm install
npm run dev









