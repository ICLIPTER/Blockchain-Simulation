import axios from "axios";
const API = "http://127.0.0.1:8000";

export async function fetchChain() {
  const res = await axios.get(`${API}/chain`);
  return res.data.chain;
}
export async function createWallet(name) {
  const res = await axios.post(`${API}/wallets/${encodeURIComponent(name)}`);
  return res.data;
}
export async function listWallets() {
  const res = await axios.get(`${API}/wallets`);
  return res.data;
}
export async function getBalance(pubkey) {
  const res = await axios.get(`${API}/balance/${encodeURIComponent(pubkey)}`);
  return res.data;
}
export async function sendTx({ sender_name, recipient_pub, amount, fee=0 }) {
  const res = await axios.post(`${API}/tx`, { sender_name, recipient_pub, amount, fee });
  return res.data;
}
export async function mine(miner_name) {
  const res = await axios.post(`${API}/mine/${encodeURIComponent(miner_name)}`);
  return res.data;
}
