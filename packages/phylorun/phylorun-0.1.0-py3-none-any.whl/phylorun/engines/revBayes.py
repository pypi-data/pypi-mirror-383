from pathlib import Path
import subprocess
from typing import Optional

from loguru import logger
from phylorun.engines.engine import Engine


class RevBayes(Engine):
    def name(self) -> str:
        """Returns the name of the engine as used in the CLI."""
        return "revbayes"

    def can_run_analysis(self, analysis_file: Path) -> bool:
        """Checks if RevBayes can run the analysis in the given file."""
        if not analysis_file.name.endswith(".rev"):
            logger.debug("No Rev file: wrong file extension (.rev requried).")
            return False

        logger.debug("RevBayes file found.")
        return True

    def run_local_analysis(
        self,
        analysis_file: Path,
        engine_path: Optional[str] = None,
        additional_cli_args: Optional[list[str]] = None,
    ):
        """Runs the analysis in the given file using the locally installed engine."""
        engine_path = engine_path or "rb"
        if not engine_path:
            raise Exception("No RevBayes binary found.")

        additional_cli_args = additional_cli_args or []

        subprocess.run([engine_path, *additional_cli_args, analysis_file])

    def run_containerized_analysis(
        self, analysis_file: Path, additional_cli_args: Optional[list[str]] = None
    ):
        """Runs the analysis in the given file in a container. This does not require the
        engine to be installed on the system."""
        logger.info("Run container RevBayes")
        raise NotImplementedError
