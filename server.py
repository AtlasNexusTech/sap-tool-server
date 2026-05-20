"""
SAP Tool Server — Reverse proxy with markup for AceDataCloud tools.

Published on SAP mainnet (agent FHTLFvs...) with 3 tools:
  - acedatacloud-search  → Google Search via AceDataCloud
  - acedatacloud-chat    → GPT-4o-mini via AceDataCloud
  - acedatacloud-images  → AI image generation via AceDataCloud

How it works:
  1. Other SAP agents discover our tools
  2. They POST to our endpoints
  3. We respond 402 Payment Required with our marked-up price
  4. Agent pays via x402 (Solana USDC) → our wallet
  5. We proxy the request to AceDataCloud (at our cost)
  6. We return the result → profit = markup

Deploy:
  pip install fastapi uvicorn acedatacloud acedatacloud-x402
  python server.py
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from acedatacloud import AceDataCloud
from acedatacloud_x402 import create_x402_payment_handler, SolanaKeypairSigner

# ─── Config ──────────────────────────────────────────────────
AGENT_PDA = "FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer"
WALLET_ADDRESS = "45Y2ShED3GyPQEhfaPq68Z6GAmdDtVh5Qrt9WjCDCadt"

# Pricing: our cost + markup
PRICING = {
    "search":  {"cost": 0.030, "price": 0.050, "description": "Web search via AceDataCloud"},
    "chat":    {"cost": 0.060, "price": 0.100, "description": "GPT-4o-mini AI analysis"},
    "images":  {"cost": 0.005, "price": 0.010, "description": "AI image generation"},
}

# ─── App ─────────────────────────────────────────────────────
app = FastAPI(
    title="SAP Tool Server — Atlas Nexus",
    description="Reverse proxy for AceDataCloud tools with x402 payments. Published on SAP mainnet.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tool-server")

# ─── AceDataCloud client (our cost) ──────────────────────────
try:
    key = os.getenv("SOLANA_PRIVATE_KEY_BASE58")
    signer = SolanaKeypairSigner.from_base58(key)
    handler = create_x402_payment_handler(network="solana", solana_signer=signer)
    ace = AceDataCloud(payment_handler=handler)
    logger.info("✅ AceDataCloud client ready (x402)")
except Exception as e:
    logger.warning(f"⚠️ AceDataCloud not configured: {e}")
    ace = None

# ─── Models ──────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

class ImageRequest(BaseModel):
    prompt: str
    style: str = "realistic"
    size: str = "1024x1024"

# ─── 402 Payment Helper ──────────────────────────────────────
def payment_required(service: str) -> JSONResponse:
    """Return 402 with x402 payment details."""
    pricing = PRICING[service]
    return JSONResponse(
        status_code=402,
        content={
            "error": "Payment Required",
            "protocol": "x402",
            "amount_usdc": pricing["price"],
            "receiver": WALLET_ADDRESS,
            "service": service,
            "description": pricing["description"],
        },
        headers={"X-Payment-Protocol": "x402", "X-Payment-Amount": str(pricing["price"])},
    )

# ─── Endpoints ───────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "server": "SAP Tool Server — Atlas Nexus",
        "agent_pda": AGENT_PDA,
        "wallet": WALLET_ADDRESS,
        "tools": [
            {"name": f"acedatacloud-{svc}", "price_usdc": p["price"],
             "cost_usdc": p["cost"], "margin": f"+{((p['price']-p['cost'])/p['cost']*100):.0f}%"}
            for svc, p in PRICING.items()
        ],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok" if ace else "degraded",
        "ace_connected": ace is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── Tool: Search ────────────────────────────────────────────
@app.post("/tools/acedatacloud-search")
def tool_search(req: SearchRequest, raw: Request):
    """Search tool — proxy to AceDataCloud with 67% markup."""
    logger.info(f"🔍 Search requested: {req.query[:60]}...")

    # Check x402 payment header (in production, verify on-chain)
    payment = raw.headers.get("X-Payment-Signature")
    if not payment:
        return payment_required("search")

    if not ace:
        raise HTTPException(503, "AceDataCloud backend unavailable")

    try:
        result = ace.search.google(query=req.query)
        organic = result.get("organic_results", [])
        results = [
            {"title": r.get("title", ""), "snippet": r.get("snippet", ""), "url": r.get("link", "")}
            for r in organic[:req.max_results]
        ]
        return {
            "service": "acedatacloud-search",
            "query": req.query,
            "results": results,
            "price_usdc": PRICING["search"]["price"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(502, f"Backend error: {e}")


# ─── Tool: Chat ──────────────────────────────────────────────
@app.post("/tools/acedatacloud-chat")
def tool_chat(req: ChatRequest, raw: Request):
    """Chat tool — proxy to AceDataCloud GPT-4o-mini with 67% markup."""
    logger.info(f"🤖 Chat requested: {req.prompt[:60]}...")

    payment = raw.headers.get("X-Payment-Signature")
    if not payment:
        return payment_required("chat")

    if not ace:
        raise HTTPException(503, "AceDataCloud backend unavailable")

    try:
        messages = [{"role": "user", "content": req.prompt}]
        if req.context:
            messages.insert(0, {"role": "system", "content": req.context})

        resp = ace.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2000,
        )
        analysis = resp["choices"][0]["message"]["content"]
        return {
            "service": "acedatacloud-chat",
            "analysis": analysis,
            "model": "gpt-4o-mini",
            "price_usdc": PRICING["chat"]["price"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(502, f"Backend error: {e}")


# ─── Tool: Images ────────────────────────────────────────────
@app.post("/tools/acedatacloud-images")
def tool_images(req: ImageRequest, raw: Request):
    """Image tool — proxy to AceDataCloud with 100% markup."""
    logger.info(f"🎨 Image requested: {req.prompt[:60]}...")

    payment = raw.headers.get("X-Payment-Signature")
    if not payment:
        return payment_required("images")

    if not ace:
        raise HTTPException(503, "AceDataCloud backend unavailable")

    try:
        task = ace.images.generate(
            provider="nano-banana",
            prompt=req.prompt,
            wait=False,
        )
        return {
            "service": "acedatacloud-images",
            "task_id": str(task) if task else "pending",
            "prompt": req.prompt,
            "price_usdc": PRICING["images"]["price"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Image failed: {e}")
        raise HTTPException(502, f"Backend error: {e}")


# ─── Main ────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🚀 SAP Tool Server starting on port {port}")
    logger.info(f"   Search: ${PRICING['search']['price']:.2f} (cost: ${PRICING['search']['cost']:.2f})")
    logger.info(f"   Chat:   ${PRICING['chat']['price']:.2f} (cost: ${PRICING['chat']['cost']:.2f})")
    logger.info(f"   Images: ${PRICING['images']['price']:.2f} (cost: ${PRICING['images']['cost']:.2f})")
    uvicorn.run(app, host="0.0.0.0", port=port)
