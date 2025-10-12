"""
Composite judge that combines multiple judges with weighted scoring.

Allows creating sophisticated evaluation strategies by combining different
judge types (e.g., reference-based + LLM-based) with custom weights.
"""

import asyncio
from typing import Dict, List, Optional, Tuple

from ..._cancellation_token import CancellationToken
from ...types import EvalScore, EvalTrajectory
from ._base import BaseEvalJudge


class CompositeJudge(BaseEvalJudge):
    """Combines multiple judges with weighted scores.

    This judge runs multiple evaluation judges in parallel and combines
    their scores using specified weights. Useful for creating multi-faceted
    evaluation strategies.

    Example:
        # 60% weight on accuracy (exact match), 40% on style (LLM judge)
        composite = CompositeJudge([
            (ExactMatchJudge(), 0.6),
            (LLMEvalJudge(client, default_criteria=["style"]), 0.4)
        ])
    """

    def __init__(
        self,
        judges: List[Tuple[BaseEvalJudge, float]],
        name: str = "Composite",
        normalize_weights: bool = True,
        answer_strategy: str = "last_non_empty",
    ):
        """Initialize the composite judge.

        Args:
            judges: List of (judge, weight) tuples
            name: Human-readable name for this judge
            normalize_weights: Whether to normalize weights to sum to 1.0
            answer_strategy: How to extract answer (passed to base, but sub-judges use their own)

        Raises:
            ValueError: If weights are invalid or no judges provided
        """
        super().__init__(name, answer_strategy)

        if not judges:
            raise ValueError("CompositeJudge requires at least one judge")

        total_weight = sum(weight for _, weight in judges)

        if total_weight <= 0:
            raise ValueError(f"Total weight must be positive, got {total_weight}")

        if normalize_weights:
            self.judges = [(judge, weight / total_weight) for judge, weight in judges]
        else:
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError(
                    f"Weights must sum to 1.0 when normalize_weights=False, got {total_weight}"
                )
            self.judges = judges

    async def score(
        self,
        trajectory: EvalTrajectory,
        criteria: Optional[List[str]] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> EvalScore:
        """Score trajectory using all judges and combine weighted results.

        Args:
            trajectory: The execution trajectory to score
            criteria: Optional criteria passed to all judges
            cancellation_token: Optional token to cancel scoring

        Returns:
            EvalScore with weighted combination of all judge scores
        """
        scores = await asyncio.gather(
            *[
                judge.score(trajectory, criteria, cancellation_token)
                for judge, _ in self.judges
            ]
        )

        overall = sum(
            score.overall * weight for score, (_, weight) in zip(scores, self.judges)
        )

        dimensions: Dict[str, float] = {}
        for score, (_, weight) in zip(scores, self.judges):
            for dim, val in score.dimensions.items():
                dimensions[dim] = dimensions.get(dim, 0.0) + (val * weight)

        reasoning: Dict[str, str] = {}
        for score, (judge, weight) in zip(scores, self.judges):
            judge_name = judge.name
            for dim, reason in score.reasoning.items():
                key = f"{dim} ({judge_name})"
                reasoning[key] = f"[weight: {weight:.2f}] {reason}"

        metadata = {
            "judge": self.name,
            "sub_judges": [
                {"name": judge.name, "weight": weight, "score": score.overall}
                for (judge, weight), score in zip(self.judges, scores)
            ],
        }

        return EvalScore(
            overall=overall,
            dimensions=dimensions,
            reasoning=reasoning,
            trajectory=trajectory,
            metadata=metadata,
        )
