"""
REPLACE THIS — this is where your agent's actual decision logic goes.

Every time the agent receives a proposal request on ``POST /api/propose``,
the runtime hands an :class:`EvaluationRequest` to this class and expects
back an :class:`EvaluationResult` — your vote, your confidence, and an
optional rationale and evidence links.

The stub below approves everything at the agent's configured default
confidence. Replace it with something real:

- Run your test suite and vote based on pass/fail
- Query a database or API for signals
- Call an LLM and parse its response
- Inspect a git commit, a PR diff, a build artifact
- Whatever your agent is an expert at

What matters is that the returned :class:`Vote` and ``confidence`` in
``[0, 1]`` honestly reflect your belief about the proposed action.
Downstream calibration scoring (Brier score) grades your honesty over
time — agents that are well-calibrated earn weight, agents that overclaim
lose weight.
"""
from __future__ import annotations

from adp_agent import AgentConfig, EvaluationRequest, EvaluationResult, Evaluator


class MyEvaluator(Evaluator):
    def __init__(self, config: AgentConfig) -> None:
        self._config = config

    async def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: REPLACE THIS STUB.
        #
        # Example: run tests and vote based on exit code.
        #
        #     proc = await asyncio.create_subprocess_shell(
        #         f"pytest {request.action.target}",
        #         stdout=asyncio.subprocess.PIPE,
        #         stderr=asyncio.subprocess.PIPE,
        #     )
        #     await proc.wait()
        #     if proc.returncode == 0:
        #         return EvaluationResult.approve(
        #             confidence=0.85, rationale="All tests pass"
        #         )
        #     return EvaluationResult.reject(
        #         confidence=0.85, rationale=f"Tests failed: exit {proc.returncode}"
        #     )

        return EvaluationResult(
            vote=self._config.default_vote,
            confidence=self._config.default_confidence,
            rationale="stub evaluator — replace MyEvaluator.evaluate with real decision logic",
        )
