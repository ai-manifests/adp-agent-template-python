# adp-agent-template-python

A forkable Python 3.11+ starter for building an [Agent Deliberation Protocol](https://adp-manifest.dev) agent on the Python / FastAPI runtime. Clone this, edit `agents/example.json` and `src/my_adp_agent/evaluator.py`, and you have a federation-ready agent.

Depends on [`adp-agent`](https://github.com/ai-manifests/adp-agent-python) from the Gitea PyPI feed.

## 30-second quickstart

```bash
# 1. Clone
git clone https://github.com/ai-manifests/adp-agent-template-python.git my-adp-agent
cd my-adp-agent

# 2. Install (pip reads pip.conf for the Gitea index)
export PIP_CONFIG_FILE=$(pwd)/pip.conf
pip install -e '.[dev]'

# 3. Generate a bearer token
export ADP_BEARER_TOKEN=$(openssl rand -hex 32)

# 4. Run
my-adp-agent agents/example.json
```

Visit `http://localhost:3000/healthz` — you should see `{"status":"ok","agentId":"did:adp:my-agent-v1"}`.

Also try:
- `http://localhost:3000/.well-known/adp-manifest.json`
- `http://localhost:3000/.well-known/adp-calibration.json` (503 until you configure a signing key — see below)

## What to edit

### 1. `agents/example.json` — your agent's identity

```json
{
  "agentId": "did:adp:my-agent-v1",
  "port": 3000,
  "domain": "my-agent.example.com",
  "decisionClasses": ["code.correctness"],
  "authorities": { "code.correctness": 0.7 },
  "stakeMagnitude": "medium",
  "defaultVote": "approve",
  "defaultConfidence": 0.65,
  "dissentConditions": [
    "if any test marked critical regresses"
  ],
  "journalDir": "./journal",
  "journalBackend": "jsonl"
}
```

Rename the file and pass a different path as the argument to `my-adp-agent` if you want multiple configs side by side.

### 2. `src/my_adp_agent/evaluator.py` — your decision logic

This is the only file where you write real code. Every time the agent receives `POST /api/propose`, the runtime calls `MyEvaluator.evaluate` with the action, decision class, and reversibility tier. Your job is to return an `EvaluationResult` — a vote, a confidence in `[0, 1]`, and a rationale.

The stub approves everything at the configured default confidence. Replace it with something real:

```python
async def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
    proc = await asyncio.create_subprocess_shell(
        f"pytest {request.action.target}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.wait()
    if proc.returncode == 0:
        return EvaluationResult.approve(confidence=0.85, rationale="All tests pass")
    return EvaluationResult.reject(confidence=0.85, rationale=f"Tests failed: exit {proc.returncode}")
```

### 3. Signed calibration snapshots (optional but strongly recommended)

Generate an Ed25519 key pair and set it via env vars:

```bash
python -c "from adp_agent import generate_key_pair; pub, priv = generate_key_pair(); print(f'ADP_PRIVATE_KEY={priv}'); print(f'ADP_PUBLIC_KEY={pub}')"
```

Copy the two values into your environment and restart. `/.well-known/adp-calibration.json` will start returning a signed snapshot covering every declared decision class.

### 4. Optional: Neo3 chain anchoring

Uncomment the `adp-agent-anchor` dependency in `pyproject.toml`, then extend `src/my_adp_agent/__main__.py` to wire up a `CalibrationAnchorScheduler`:

```python
from adp_agent_anchor import BlockchainStoreFactory, CalibrationAnchorScheduler

# ... after constructing host ...
if config.calibration_anchor and config.calibration_anchor.enabled:
    store = BlockchainStoreFactory.create(config.calibration_anchor)
    if store:
        scheduler = CalibrationAnchorScheduler(config, host.journal, store)
        host.after_start(scheduler.start)
        host.before_stop(scheduler.stop)
```

Targets: `mock`, `neo-express`, `neo-custom`, `neo-testnet`, `neo-mainnet`. Same code, same smart contract, only the RPC URL and signing wallet change.

## Docker

A multi-stage Dockerfile and a docker-compose.yml are included for production deployment.

```bash
# Build + run
docker compose up --build

# Or build the image directly
docker build -t my-adp-agent:latest .
docker run -p 3000:3000 \
  -e ADP_BEARER_TOKEN=$(openssl rand -hex 32) \
  -v $(pwd)/journal:/app/journal \
  my-adp-agent:latest
```

## PyPI feed

`adp-agent` is published to the `ai-manifests` Gitea PyPI feed. The `pip.conf` at the repo root configures pip to use that feed as an extra index (falling back to public PyPI for everything else). Activate it by setting `PIP_CONFIG_FILE=$(pwd)/pip.conf` in your shell before running `pip install`, or copy it to your user-level pip config.

## Federation checklist

Once your agent is running locally, to join a real federation:

1. Put your agent behind HTTPS at a stable domain (the `domain` field in your config must resolve)
2. Share the URL to `/.well-known/adp-manifest.json` with the registry or with peers
3. Implement a real `MyEvaluator` that reflects genuine expertise — agents that fake calibration lose weight fast
4. Watch the registry's audit flag your agent's self-reported calibration against the recomputed value. If the two match, you're calibrated. If they diverge, your agent is lying and will lose weight over time.

## License

Apache-2.0 — see [`LICENSE`](LICENSE) for the full license text and [`NOTICE`](NOTICE) for attribution. Fork freely; your own agent code (the parts you add on top of the template) is yours to license however you want, as long as the original `LICENSE` and `NOTICE` files remain with the template content you redistribute unchanged (per Apache-2.0 §4).
