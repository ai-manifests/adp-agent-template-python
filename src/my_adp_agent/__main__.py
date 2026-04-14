"""
Entry point for my-adp-agent. Loads the agent config from a JSON file,
applies environment variable overrides for secrets, constructs an
:class:`AdpAgentHost`, registers the adopter's :class:`MyEvaluator`, and
runs the host until shutdown.

Usage:

    python -m my_adp_agent agents/example.json

Or via the installed console script:

    my-adp-agent agents/example.json
"""
from __future__ import annotations

import asyncio
import dataclasses
import json
import os
import sys
from pathlib import Path

from adp_agent import (
    AdpAgentHost,
    AgentConfig,
    AuthConfig,
    JournalBackend,
)
from adp_manifest import StakeMagnitude, Vote

from .evaluator import MyEvaluator


def load_config(path: Path) -> AgentConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))

    return AgentConfig(
        agent_id=raw["agentId"],
        port=int(raw["port"]),
        domain=raw["domain"],
        decision_classes=tuple(raw["decisionClasses"]),
        authorities=dict(raw["authorities"]),
        stake_magnitude=StakeMagnitude(raw["stakeMagnitude"]),
        default_vote=Vote(raw["defaultVote"]),
        default_confidence=float(raw["defaultConfidence"]),
        dissent_conditions=tuple(raw["dissentConditions"]),
        journal_dir=raw["journalDir"],
        journal_backend=JournalBackend(raw.get("journalBackend", "jsonl")),
    )


def apply_env_overrides(config: AgentConfig) -> AgentConfig:
    bearer = os.environ.get("ADP_BEARER_TOKEN")
    private_key = os.environ.get("ADP_PRIVATE_KEY")
    public_key = os.environ.get("ADP_PUBLIC_KEY")

    if bearer or private_key or public_key:
        return dataclasses.replace(
            config,
            auth=AuthConfig(
                bearer_token=bearer or "",
                private_key=private_key,
                public_key=public_key,
            ),
        )
    return config


async def run(config_path: Path) -> None:
    config = load_config(config_path)
    config = apply_env_overrides(config)
    host = AdpAgentHost(config, evaluator=MyEvaluator(config))
    await host.run()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m my_adp_agent <config.json>", file=sys.stderr)
        sys.exit(1)
    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(config_path))


if __name__ == "__main__":
    main()
