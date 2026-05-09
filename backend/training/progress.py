from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import TextIO


@dataclass(frozen=True)
class ProgressStage:
    index: int
    total: int
    name: str

    @property
    def prefix(self) -> str:
        return f"{self.index}/{self.total} {self.name}"


class TrainingProgress:
    def __init__(self, total_steps: int, stream: TextIO | None = None):
        self.total_steps = total_steps
        self.stream = stream or sys.stdout
        self._current_index = 0
        self._current_stage: ProgressStage | None = None

    def start_step(self, name: str, detail: str | None = None) -> ProgressStage:
        self._current_index += 1
        self._current_stage = ProgressStage(
            index=self._current_index,
            total=self.total_steps,
            name=name,
        )
        self._write(self._line(self._current_stage, "running", detail=detail))
        return self._current_stage

    def finish_step(self, **metrics) -> None:
        if self._current_stage is None:
            raise RuntimeError("finish_step called before start_step")

        self._write(
            self._line(
                self._current_stage,
                "done",
                detail=self._format_metrics(metrics),
            )
        )
        self._current_stage = None

    def metric(self, **metrics) -> None:
        if self._current_stage is None:
            raise RuntimeError("metric called before start_step")

        detail = self._format_metrics(metrics)
        if detail:
            self._write(self._line(self._current_stage, "info", detail=detail))

    def _line(self, stage: ProgressStage, status: str, detail: str | None = None) -> str:
        parts = [stage.prefix, status]
        if detail:
            parts.append(detail)
        return "  ".join(parts)

    def _format_metrics(self, metrics) -> str:
        return " ".join(
            f"{key}={self._format_value(value)}"
            for key, value in metrics.items()
            if value is not None
        )

    def _format_value(self, value) -> str:
        if isinstance(value, float):
            return f"{value:.4f}"
        return str(value)

    def _write(self, message: str) -> None:
        print(message, file=self.stream)
