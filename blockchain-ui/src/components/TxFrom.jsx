import React, { useState } from "react";
import { sendTx } from "../api";

export default function TxForm() {
  const [sender, setSender] = useState("");
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  const [fee, setFee] = useState("0");

  async function submit(e) {
    e.preventDefault();
    if (!sender || !recipient || !amount) {
      alert("fill fields");
      return;
    }
    try {
      const res = await sendTx({ sender_name: sender, recipient_pub: recipient, amount: parseFloat(amount), fee: parseFloat(fee) });
      alert("Tx added");
      setRecipient(""); setAmount(""); setFee("0");
    } catch (err) {
      alert(err?.response?.data?.detail || "Error creating tx");
    }
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Send Transaction</h2>
      <form className="space-y-2" onSubmit={submit}>
        <input value={sender} onChange={e=>setSender(e.target.value)} placeholder="sender (wallet name)" className="w-full border p-2 rounded"/>
        <input value={recipient} onChange={e=>setRecipient(e.target.value)} placeholder="recipient public hex" className="w-full border p-2 rounded"/>
        <div className="flex gap-2">
          <input value={amount} onChange={e=>setAmount(e.target.value)} placeholder="amount" className="w-1/2 border p-2 rounded"/>
          <input value={fee} onChange={e=>setFee(e.target.value)} placeholder="fee" className="w-1/2 border p-2 rounded"/>
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded">Send</button>
      </form>
    </div>
  );
}
