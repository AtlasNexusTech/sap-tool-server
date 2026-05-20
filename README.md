# 🔮 SAP Tool Server — Atlas Nexus

**Reverse proxy for AceDataCloud tools with x402 payments and built-in profit margin.**

Published on **SAP mainnet** (Synapse Agent Protocol) via agent [`FHTLFvs...`](https://solscan.io/account/FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer). Other autonomous agents discover our tools, pay via x402, and we proxy to AceDataCloud — keeping the spread.

```
Agent → discovers tool on SAP → calls our server → pays 402 → we proxy → profit
```

---

## 💰 Pricing (with markup)

| Tool | Our Cost | Selling Price | Margin | What it does |
|------|----------|---------------|--------|--------------|
| `acedatacloud-search` | $0.030 | **$0.050** | +67% | Google web search |
| `acedatacloud-chat` | $0.060 | **$0.100** | +67% | GPT-4o-mini AI analysis |
| `acedatacloud-images` | $0.005 | **$0.010** | +100% | AI image generation |

### Revenue projection

| Agents using tools | Calls/day | Daily revenue | Monthly revenue |
|-------------------|-----------|---------------|-----------------|
| 1 agent | 10 | $0.65 | $19.50 |
| 5 agents | 50 | $3.25 | $97.50 |
| 10 agents | 100 | $6.50 | **$195.00** |

---

## 🚀 Quick Start

```bash
git clone https://github.com/AtlasNexusTech/sap-tool-server.git
cd sap-tool-server
pip install -r requirements.txt
cp .env.example .env
# Edit .env → add SOLANA_PRIVATE_KEY_BASE58

python server.py
# → http://localhost:8000
# → Swagger docs: http://localhost:8000/docs
```

---

## 🔄 How It Works

### Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Agent discovers tool on SAP explorer                     │
│     ↓                                                        │
│  2. Agent POSTs to our /tools/{tool-name} endpoint           │
│     ↓                                                        │
│  3. Server responds 402 Payment Required ($0.05 USDC)        │
│     ↓                                                        │
│  4. Agent signs Solana transaction → sends payment proof     │
│     ↓                                                        │
│  5. Server verifies payment → proxies to AceDataCloud        │
│     ↓                                                        │
│  6. AceDataCloud responds (cost us $0.03)                    │
│     ↓                                                        │
│  7. Server returns result to agent                           │
│     ↓                                                        │
│  💰 Profit: $0.05 - $0.03 = $0.02 per call                  │
└──────────────────────────────────────────────────────────────┘
```

### Endpoints

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/tools/acedatacloud-search` | POST | $0.050 | Web search |
| `/tools/acedatacloud-chat` | POST | $0.100 | AI chat analysis |
| `/tools/acedatacloud-images` | POST | $0.010 | Image generation |
| `/health` | GET | Free | Server health |
| `/docs` | GET | Free | Swagger UI |

---

## 🔗 SAP Mainnet Info

| Property | Value |
|----------|-------|
| Agent PDA | `FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer` |
| Program | `SAPpUhsWLJG1FfkGRcXagEDMrMsWGjbky7AyhGpFETZ` |
| Wallet | `45Y2ShED3GyPQEhfaPq68Z6GAmdDtVh5Qrt9WjCDCadt` |
| Tools published | 8 (3 AceDataCloud + 5 Seedance) |
| Stake | 0.1 SOL |

---

## 🛠️ Architecture

```
sap-tool-server/
├── server.py          # FastAPI server with x402 reverse proxy
├── requirements.txt   # Python dependencies
├── .env.example       # Configuration template
├── README.md          # This file
└── docs/              # GitHub Pages website
    └── index.html     # Landing page
```

---

## 🔒 Security

- **x402 payments**: Every API call requires a Solana-signed payment
- **402 Payment Required**: Standard HTTP status with x402 protocol headers
- **No API keys stored**: Server uses Solana keypair for outbound payments only
- **Stateless**: No user data stored — pure proxy

---

## 📄 License

MIT — Atlas Nexus ([AtlasNexusTech](https://github.com/AtlasNexusTech))

---

## Built by

🔮 **Atlas Nexus** — Autonomous agent infrastructure  
Powered by OOBE Protocol Synapse × AceDataCloud × x402 × Solana
