import React, { useState, useEffect } from "react";
import { createWallet, listWallets } from "../api";

export default function Wallets({ onWallets }) {
  const [name, setName] = useState("");
  const [wallets, setWallets] = useState({});

  useEffect(() => {
    (async () => {
      const w = await listWallets();
      setWallets(w);
      onWallets && onWallets(w);
    })();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!name) return;
    const res = await createWallet(name);
    const updated = await listWallets();
    setWallets(updated);
    onWallets && onWallets(updated);
    setName("");
    alert(`Created ${res.name}\npublic: ${res.public_key}\n(private shown once)`);
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Wallets</h2>
      <form onSubmit={handleCreate} className="flex gap-2 mb-4">
        <input value={name} onChange={e=>setName(e.target.value)} placeholder="wallet name" className="border p-2 rounded w-full"/>
        <button className="bg-blue-600 text-white px-3 rounded">Create</button>
      </form>

      <ul className="space-y-2">
        {Object.entries(wallets).map(([k, pub]) => (
          <li key={k} className="flex justify-between items-center border p-2 rounded">
            <div>
              <div className="font-medium">{k}</div>
              <div className="text-xs text-gray-600">{pub.slice(0, 18)}...</div>
            </div>
            <div className="text-sm text-gray-700">pub</div>
          </li>
        ))}
        {Object.keys(wallets).length === 0 && <div className="text-sm text-gray-500">No wallets yet</div>}
      </ul>
    </div>
  );
}
