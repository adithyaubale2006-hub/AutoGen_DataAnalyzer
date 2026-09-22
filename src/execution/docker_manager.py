from dataclasses import dataclass


@dataclass
class DockerManager:
	image: str = "python:3.11-slim"

	def is_available(self) -> bool:
		try:
			import docker

			docker.from_env().ping()
			return True
		except Exception:
			return False
