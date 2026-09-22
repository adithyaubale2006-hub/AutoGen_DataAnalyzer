from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AnalysisState:
	source_path: Path
	output_dir: Path
	status: str = "ready"
	errors: list[str] = field(default_factory=list)
	artifacts: dict[str, Path] = field(default_factory=dict)
	metrics: dict[str, Any] = field(default_factory=dict)

	def fail(self, message: str) -> None:
		self.status = "failed"
		self.errors.append(message)

	def complete(self) -> None:
		self.status = "complete"
