"""Local executor: run a docker image locally and collect output."""

import subprocess
import time
import logging
from .base_executor import BaseExecutor
from ..models import CodeResult
from ..settings import settings
from ..kpi_extractor import extract_kpi_from_stdout

class LocalExecutor(BaseExecutor):
    """Execute code locally by running a docker image and collecting output."""

    @property
    def platform_name(self) -> str:
        return "local"

    def execute(self, docker_image_tag: str) -> CodeResult:
        """
        Execute a docker image locally and collect output.

        Args:
            docker_image_tag: The tag of the docker image to run.

        Returns:
            CodeResult containing stdout, stderr, return_code, runtime_ms, and kpi.
        """
        start_time = time.time()
        
        # Build docker run command with optional volume mounting
        run_cmd = ["docker", "run", "--rm"]
        
        # Add volume mount if data_volume is specified in config
        if self.config and self.config.get('data_volume'):
            data_volume = self.config['data_volume']
            logging.info(f"Mounting data volume: {data_volume} -> /data")
            run_cmd.extend(["-v", f"{data_volume}:/data"])
            run_cmd.extend(["-e", "INPUT_URI=/data"])
        
        run_cmd.append(docker_image_tag)
        logging.info(f"Running docker image locally: {docker_image_tag}")
        try:
            output = subprocess.run(
                run_cmd,
                capture_output=True,
                text=True,
                timeout=settings.script_execution_timeout
            )
            return_code = output.returncode
            out = output.stdout
            err = output.stderr
        except subprocess.TimeoutExpired:
            return_code = -9
            out = None
            err = f"Process timed out after {settings.script_execution_timeout} seconds"
            logging.info(f"Process timed out after {settings.script_execution_timeout} seconds")
        except Exception as e:
            return_code = -1
            out = None
            err = f"Error running docker image: {e}"
            logging.error(err)

        # Clean up empty strings
        if isinstance(out, str) and out.strip() == "":
            out = None
        if isinstance(err, str) and err.strip() == "":
            err = None

        logging.info(f"Docker execution stdout: {out}")
        logging.info(f"Docker execution stderr: {err}")

        runtime_ms = int((time.time() - start_time) * 1000)
        kpi = extract_kpi_from_stdout(out) if out else None

        # Note: Docker image cleanup is handled by workflow_runner, not by the executor
        
        return CodeResult(
            stdout=out,
            stderr=err,
            return_code=return_code,
            runtime_ms=runtime_ms,
            kpi=kpi
        )

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
