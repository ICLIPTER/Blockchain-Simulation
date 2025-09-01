import { useState, useEffect } from "react";

export default function App() {
  const [wallets, setWallets] = useState([]);
  const [chain, setChain] = useState([]);
  // const [balance, setBalance] = useState({});
  
  // Fetch example data from backend (later)
  useEffect(() => {
    // TODO: Replace URL with your FastAPI server endpoint
    fetch("http://localhost:8000/chain")
      .then(res => res.json())
      .then(data => setChain(data.chain || []));
    
    fetch("http://localhost:8000/wallets")
      .then(res => res.json())
      .then(data => setWallets(data.wallets || []));
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-4xl font-bold mb-6">🧱 Mini Blockchain Dashboard</h1>

      <section className="mb-6">
        <h2 className="text-2xl font-semibold mb-2">Wallets</h2>
        <ul className="list-disc list-inside">
          {wallets.length === 0 ? (
            <li>No wallets yet</li>
          ) : (
            wallets.map((w, idx) => <li key={idx}>{w.name} — {w.balance} coins</li>)
          )}
        </ul>
      </section>

      <section className="mb-6">
        <h2 className="text-2xl font-semibold mb-2">Blockchain</h2>
        <ul className="max-h-64 overflow-y-auto border border-gray-700 p-4 rounded">
          {chain.length === 0 ? (
            <li>No blocks yet</li>
          ) : (
            chain.map((block, idx) => (
              <li key={idx} className="mb-2 p-2 border border-gray-600 rounded">
                <div>Index: {block.index}</div>
                <div>Timestamp: {block.timestamp}</div>
                <div>Transactions: {block.transactions.length}</div>
                <div>Hash: {block.hash.slice(0, 20)}...</div>
              </li>
            ))
          )}
        </ul>
      </section>
    </div>
  );
}
