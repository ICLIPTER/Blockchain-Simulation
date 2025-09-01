# server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mini_blockchain import Blockchain, Wallet, Transaction

# ----------------------------
# Create global blockchain and wallets
# ----------------------------
blockchain = Blockchain()

# create some default wallets with real ECDSA keys
alice = Wallet("alice")
bob = Wallet("bob")
miner = Wallet("miner")

wallets = {
    "alice": alice,
    "bob": bob,
    "miner": miner
}

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(title="Mini Blockchain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Endpoints
# ----------------------------
@app.get("/chain")
def get_chain():
    return {"chain": blockchain.blocks}

@app.get("/wallets")
def get_wallets():
    return {
        "wallets": [
            {"name": w.name, "public_key": w.export_public_hex(), "balance": w.balance()}
            for w in wallets.values()
        ]
    }

@app.post("/tx")
def create_transaction(sender: str, recipient_pubhex: str, amount: float):
    if sender not in wallets:
        raise HTTPException(status_code=400, detail="Sender wallet not found")
    tx = Transaction(sender=wallets[sender], recipient_pub=recipient_pubhex, amount=amount)
    tx.sign(wallets[sender])
    blockchain.add_transaction(tx)
    return {"status": "success", "transaction": tx.to_dict()}

@app.post("/mine")
def mine_block(miner_name: str):
    if miner_name not in wallets:
        raise HTTPException(status_code=400, detail="Miner wallet not found")
    reward_tx = blockchain.mine(miner=wallets[miner_name])
    return {"status": "success", "reward": reward_tx.to_dict() if reward_tx else None}
