"""
mini_blockchain_crypto.py

Upgraded mini blockchain with:
- Real ECDSA (SECP256k1) signing & verification using `ecdsa` package.
- Transaction signature verification before acceptance.
- Balance checks (confirmed + pending).
- Simple proof-of-work & mining reward.

Educational only. Not production-grade.
"""

import hashlib
import json
import time
import random
import sys
from typing import List, Dict, Any, Optional, Tuple

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

# -------------------------
# Utilities
# -------------------------
def sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def current_timestamp() -> float:
    return time.time()

# -------------------------
# Wallet (ECDSA)
# -------------------------
class Wallet:
    """
    ECDSA Wallet using SECP256k1.
    - private_key: SigningKey
    - public_key: hex-encoded VerifyingKey bytes
    """
    def __init__(self, sk: Optional[SigningKey] = None):
        self.sk = sk or SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.get_verifying_key()

    @staticmethod
    def from_hex_private(hex_priv: str) -> "Wallet":
        sk = SigningKey.from_string(bytes.fromhex(hex_priv), curve=SECP256k1)
        return Wallet(sk=sk)

    def export_private_hex(self) -> str:
        return self.sk.to_string().hex()

    def export_public_hex(self) -> str:
        return self.vk.to_string().hex()

    def sign(self, message: bytes) -> str:
        """
        Sign bytes and return hex signature.
        """
        sig = self.sk.sign(message)
        return sig.hex()

    @staticmethod
    def verify_signature(public_hex: str, message: bytes, signature_hex: str) -> bool:
        """
        Verify signature: return True if valid.
        """
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(public_hex), curve=SECP256k1)
            vk.verify(bytes.fromhex(signature_hex), message)
            return True
        except (BadSignatureError, Exception):
            return False

# -------------------------
# Transaction
# -------------------------
class Transaction:
    def __init__(self, sender_pub: str, recipient_pub: str, amount: float, signature: Optional[str] = None, timestamp: Optional[float] = None, fee: float = 0.0):
        self.sender = sender_pub
        self.recipient = recipient_pub
        self.amount = float(amount)
        self.fee = float(fee)
        self.timestamp = timestamp or current_timestamp()
        self.signature = signature  # hex

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

    def compute_hash(self) -> str:
        # canonical serialization without signature
        tx_json = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return sha256(tx_json)

    def sign(self, wallet: Wallet):
        """
        Sign the transaction using wallet (must match sender).
        """
        if wallet.export_public_hex() != self.sender:
            raise ValueError("Signing wallet does not match transaction sender public key.")
        tx_hash = self.compute_hash().encode()
        self.signature = wallet.sign(tx_hash)

    def is_signed(self) -> bool:
        return self.signature is not None

    def is_valid(self) -> bool:
        """
        Valid if:
         - If SYSTEM sender (mining reward), no signature required.
         - Otherwise, signature exists and verifies against sender public key.
        """
        if self.sender == "SYSTEM":
            return True
        if not self.is_signed():
            return False
        tx_hash_bytes = self.compute_hash().encode()
        return Wallet.verify_signature(self.sender, tx_hash_bytes, self.signature)

# -------------------------
# Block
# -------------------------
class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, timestamp: Optional[float] = None, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or current_timestamp()
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_merkle_root(self) -> str:
        """
        Simple merkle-like root: hash transactions pairwise until single hash remains.
        """
        tx_hashes = [tx.compute_hash() for tx in self.transactions]
        if not tx_hashes:
            return sha256("")
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:  # pad last
                tx_hashes.append(tx_hashes[-1])
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i+1]
                new_hashes.append(sha256(combined))
            tx_hashes = new_hashes
        return tx_hashes[0]

    def compute_hash(self) -> str:
        block_header = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "merkle_root": self.compute_merkle_root()
        }
        return sha256(json.dumps(block_header, sort_keys=True))

# -------------------------
# Blockchain
# -------------------------
class Blockchain:
    def __init__(self, difficulty: int = 4, mining_reward: float = 50.0):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(index=0, transactions=[], previous_hash="0", timestamp=current_timestamp(), nonce=0)
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        # Validate tx structure and signature
        if not transaction.is_valid():
            print("Rejected transaction: invalid signature or structure.")
            return False

        # Confirm sender has enough balance (considering pending txs)
        if transaction.sender != "SYSTEM":
            sender_bal = self.get_balance(transaction.sender)
            pending_spent = sum((tx.amount + tx.fee) for tx in self.pending_transactions if tx.sender == transaction.sender)
            effective_available = sender_bal - pending_spent
            if (transaction.amount + transaction.fee) > effective_available:
                print("Rejected transaction: insufficient funds (including pending transactions).")
                return False

        self.pending_transactions.append(transaction)
        return True

    def proof_of_work(self, block: Block) -> Tuple[str, int]:
        block.nonce = 0
        computed_hash = block.compute_hash()
        target = "0" * self.difficulty
        while not computed_hash.startswith(target):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash, block.nonce

    def mine_pending_transactions(self, miner_pub: str) -> Block:
        # Collect up to N transactions (optional): keep simple, include all
        txs_to_include = self.pending_transactions.copy()

        # Calculate total fees
        total_fees = sum(tx.fee for tx in txs_to_include)

        # Create reward transaction (reward + fees)
        reward_tx = Transaction(sender="SYSTEM", recipient=miner_pub, amount=self.mining_reward + total_fees)
        txs_to_include.append(reward_tx)

        new_block = Block(index=self.last_block.index + 1, transactions=txs_to_include, previous_hash=self.last_block.hash)
        print(f"Mining block {new_block.index}: {len(txs_to_include)} txs, difficulty={self.difficulty} ...")
        new_hash, nonce = self.proof_of_work(new_block)
        new_block.hash = new_hash
        new_block.nonce = nonce
        self.chain.append(new_block)

        # Clear pending transactions that were included
        self.pending_transactions = [tx for tx in self.pending_transactions if tx not in txs_to_include]

        print(f"Mined block {new_block.index} hash={new_block.hash} nonce={new_block.nonce}")
        return new_block

    def get_balance(self, pubkey: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == pubkey:
                    balance -= (tx.amount + tx.fee)
                if tx.recipient == pubkey:
                    balance += tx.amount
        return balance

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i-1]
            if cur.previous_hash != prev.hash:
                print(f"Invalid chain: block {i} previous_hash mismatch.")
                return False
            if cur.compute_hash() != cur.hash:
                print(f"Invalid chain: block {i} hash mismatch.")
                return False
            # Validate transactions
            for tx in cur.transactions:
                if not tx.is_valid():
                    print(f"Invalid transaction in block {i}: {tx.to_dict()}")
                    return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(f"--- Block {block.index} ---")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print(f"Previous: {block.previous_hash}")
            print(f"Hash:     {block.hash}")
            print(f"Nonce:    {block.nonce}")
            print(f"Merkle:   {block.compute_merkle_root()}")
            print("Transactions:")
            for tx in block.transactions:
                print(f"  {tx.sender[:8]}... -> {tx.recipient[:8]}... : {tx.amount} fee={tx.fee} sig={bool(tx.signature)}")
            print("")

# -------------------------
# Demo / CLI helpers
# -------------------------
def demo_workflow():
    print("=== Mini Blockchain (ECDSA) Demo ===")
    bc = Blockchain(difficulty=3, mining_reward=25.0)

    # Create wallets
    alice = Wallet()
    bob = Wallet()
    miner = Wallet()

    print("\nWallets (public hex shown shortened):")
    print("Alice pub:", alice.export_public_hex()[:16] + "...")
    print("Bob   pub:", bob.export_public_hex()[:16] + "...")
    print("Miner pub:", miner.export_public_hex()[:16] + "...")

    # Faucet: SYSTEM -> Alice
    faucet = Transaction(sender="SYSTEM", recipient_pub=alice.export_public_hex(), amount=100.0)

    # Note: for convenience we create SYSTEM txs without signing
    bc.add_transaction(faucet)

    # Mine to include faucet
    bc.mine_pending_transactions(miner_pub := miner.export_public_hex())

    print("\nBalances after faucet mining:")
    print("Alice:", bc.get_balance(alice.export_public_hex()))
    print("Bob:  ", bc.get_balance(bob.export_public_hex()))
    print("Miner:", bc.get_balance(miner.export_public_hex()))

    # Alice sends to Bob (with fee)
    tx1 = Transaction(sender_pub := alice.export_public_hex(), recipient_pub := bob.export_public_hex(), amount=30.0, fee=0.5)
    tx1.sign(alice)
    added = bc.add_transaction(tx1)
    print("Alice->Bob tx added:", added)

    # Try overspend (should be rejected)
    tx2 = Transaction(sender_pub, bob.export_public_hex(), amount=1000.0, fee=0.1)
    tx2.sign(alice)
    added2 = bc.add_transaction(tx2)
    print("Attempt overspend tx added (should be False):", added2)

    # Miner mines (collects fee)
    bc.mine_pending_transactions(miner.export_public_hex())

    print("\nBalances after Alice->Bob and mining:")
    print("Alice:", bc.get_balance(alice.export_public_hex()))
    print("Bob:  ", bc.get_balance(bob.export_public_hex()))
    print("Miner:", bc.get_balance(miner.export_public_hex()))

    print("\nChain valid?", bc.is_chain_valid())
    bc.print_chain()

def run_interactive():
    print("Welcome to Mini Blockchain (ECDSA) interactive demo.")
    bc = Blockchain(difficulty=3, mining_reward=25.0)
    wallets: Dict[str, Wallet] = {}

    def create_wallet(name: str) -> Wallet:
        w = Wallet()
        wallets[name] = w
        print(f"Created wallet '{name}', public_key={w.export_public_hex()[:24]}...")
        return w

    # create sample wallets
    create_wallet("alice")
    create_wallet("bob")
    create_wallet("miner")

    help_text = """
Commands:
  show_chain                       : Print blockchain
  create_wallet <name>             : Create a new wallet
  show_wallets                     : List known wallets (short pub)
  export_priv <name>               : Print private key hex for backup (keep secret!)
  tx <from> <to_pubhex> <amt> [fee]: Create & sign tx from known wallet
  mine <miner_name>                : Mine pending transactions, reward to miner_name
  balance <name_or_pubhex>         : Show balance (known name or raw pub hex)
  validate                         : Check chain validity
  help                             : This help
  exit                             : Quit
"""
    print(help_text)
    while True:
        try:
            cmd = input("cmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not cmd:
            continue
        parts = cmd.split()
        if parts[0] == "exit":
            break
        elif parts[0] == "help":
            print(help_text)
        elif parts[0] == "show_chain":
            bc.print_chain()
        elif parts[0] == "create_wallet" and len(parts) == 2:
            create_wallet(parts[1])
        elif parts[0] == "show_wallets":
            for name, w in wallets.items():
                print(name, "->", w.export_public_hex()[:24] + "...")
        elif parts[0] == "export_priv" and len(parts) == 2:
            name = parts[1]
            if name in wallets:
                print("PRIVATE_KEY (hex). Keep secret!:", wallets[name].export_private_hex())
            else:
                print("Unknown wallet.")
        elif parts[0] == "tx" and (len(parts) == 4 or len(parts) == 5):
            frm = parts[1]
            to_pub = parts[2]
            try:
                amt = float(parts[3])
            except:
                print("Invalid amount.")
                continue
            fee = float(parts[4]) if len(parts) == 5 else 0.0
            if frm not in wallets:
                print("Unknown sender wallet. Create it first.")
                continue
            tx = Transaction(sender_pub := wallets[frm].export_public_hex(), recipient_pub := to_pub, amount=amt, fee=fee)
            tx.sign(wallets[frm])
            added = bc.add_transaction(tx)
            print("Transaction added:", added)
        elif parts[0] == "mine" and len(parts) == 2:
            miner_name = parts[1]
            if miner_name not in wallets:
                print("Unknown miner wallet.")
                continue
            bc.mine_pending_transactions(wallets[miner_name].export_public_hex())
        elif parts[0] == "balance" and len(parts) == 2:
            arg = parts[1]
            if arg in wallets:
                pub = wallets[arg].export_public_hex()
            else:
                pub = arg
            print("Balance:", bc.get_balance(pub))
        elif parts[0] == "validate":
            print("Chain valid:", bc.is_chain_valid())
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--demo":
        demo_workflow()
    else:
        run_interactive()
