from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


@dataclass
class ExecutionResult:
	returncode: int
	stdout: str
	stderr: str


def execute_python(code: str, work_dir: str | Path | None = None, timeout: int = 60) -> ExecutionResult:
	completed = subprocess.run(
		[sys.executable, "-c", code],
		cwd=work_dir,
		capture_output=True,
		text=True,
		timeout=timeout,
		check=False,
	)
	return ExecutionResult(completed.returncode, completed.stdout, completed.stderr)
