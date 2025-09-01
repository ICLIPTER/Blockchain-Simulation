from fastapi import FastAPI
from pydantic import BaseModel
from mini_blockchain import Blockchain, Wallet, Transaction

app = FastAPI()
blockchain = Blockchain()
wallets = {}

class TxRequest(BaseModel):
    sender: str
    recipient: str
    amount: float

@app.get("/chain")
def get_chain():
    return [block.__dict__ for block in blockchain.chain]

@app.post("/wallets/{name}")
def create_wallet(name: str):
    wallet = Wallet()
    wallets[name] = wallet
    return {"name": name, "public_key": wallet.export_public_hex()}

@app.get("/wallets")
def list_wallets():
    return {name: w.export_public_hex() for name, w in wallets.items()}

@app.get("/balance/{pubkey}")
def get_balance(pubkey: str):
    return {"balance": blockchain.get_balance(pubkey)}

@app.post("/tx")
def create_tx(tx: TxRequest):
    if tx.sender not in wallets:
        return {"error": "Unknown sender"}
    sender_wallet = wallets[tx.sender]
    new_tx = Transaction(
        sender=sender_wallet.export_public_hex(),
        recipient=tx.recipient,
        amount=tx.amount
    )
    new_tx.sign(sender_wallet.private_key)
    blockchain.add_transaction(new_tx)
    return {"status": "Transaction added", "tx": new_tx.__dict__}

@app.post("/mine/{miner}")
def mine_block(miner: str):
    if miner not in wallets:
        return {"error": "Unknown miner"}
    blockchain.mine_pending(wallets[miner].export_public_hex())
    return {"status": "Block mined", "height": len(blockchain.chain)}
