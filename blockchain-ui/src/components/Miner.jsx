import React, { useState } from "react";
import { mine } from "../api";

export default function Miner() {
  const [miner, setMiner] = useState("");

  async function doMine() {
    if (!miner) { alert("set miner wallet name"); return; }
    try {
      await mine(miner);
      alert("Block mined");
    } catch (e) {
      alert(e?.response?.data?.detail || "error mining");
    }
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Mine</h2>
      <input value={miner} onChange={e=>setMiner(e.target.value)} placeholder="miner wallet name" className="w-full border p-2 rounded mb-2"/>
      <button onClick={doMine} className="bg-purple-600 text-white px-4 py-2 rounded">Mine Block</button>
    </div>
  );
}
