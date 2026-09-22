from dataclasses import dataclass
from pathlib import Path

from src.pipeline import run_pipeline


@dataclass
class AnalysisTeam:
	output_dir: Path

	def run(self, source: str | Path) -> dict:
		return run_pipeline(source, self.output_dir)
