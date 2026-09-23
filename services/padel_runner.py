"""
PaDEL Runner Service for PaDEL-Descriptor Streamlit Application.
Handles temporary workspace isolation, Java process invocation, and execution tracking.
"""

import os
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List


DEFAULT_JAR_PATH = Path(__file__).parent.parent / "padel" / "PaDEL-Descriptor.jar"


def run_padel_calculation(
    input_content: str,
    input_filename: str = "molecules.smi",
    use_2d: bool = True,
    use_3d: bool = False,
    use_fp: bool = True,
    threads: int = 4,
    memory_gb: int = 2,
    remove_salts: bool = False,
    standardize_nitro: bool = False,
    standardize_tautomers: bool = False,
    retain_order: bool = True,
    use_filename_as_molname: bool = False,
    timeout_sec: int = 1800,
    custom_jar_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Executes PaDEL-Descriptor Java engine inside an isolated temporary workspace.

    Returns dict with:
        success: bool
        csv_path: Optional[str]
        output_df_bytes: Optional[bytes]
        elapsed_time: float
        stdout: str
        stderr: str
        error: Optional[str]
    """
    start_time = time.time()
    jar_path = custom_jar_path or DEFAULT_JAR_PATH

    if not jar_path.exists():
        return {
            "success": False,
            "csv_path": None,
            "output_bytes": None,
            "elapsed_time": 0.0,
            "stdout": "",
            "stderr": "",
            "error": f"PaDEL JAR executable not found at '{jar_path}'.",
        }

    if not (use_2d or use_3d or use_fp):
        return {
            "success": False,
            "csv_path": None,
            "output_bytes": None,
            "elapsed_time": 0.0,
            "stdout": "",
            "stderr": "",
            "error": "At least one calculation option (2D Descriptors, 3D Descriptors, or Fingerprints) must be selected.",
        }

    # Create temporary isolated directory for the job
    with tempfile.TemporaryDirectory(prefix="padel_job_") as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        input_dir.mkdir(parents=True, exist_ok=True)

        input_file_path = input_dir / input_filename
        output_csv_path = temp_path / "descriptors.csv"

        # Write input molecular content to temp file
        if isinstance(input_content, str):
            input_file_path.write_text(input_content, encoding="utf-8")
        elif isinstance(input_content, bytes):
            input_file_path.write_bytes(input_content)

        # Build Java Command
        heap_max = f"-Xmx{max(1, memory_gb)}G"
        heap_min = "-Xms512M"

        cmd: List[str] = [
            "java",
            heap_min,
            heap_max,
            "-Djava.awt.headless=true",
            "-jar",
            str(jar_path.resolve()),
            "-dir",
            str(input_dir.resolve()),
            "-file",
            str(output_csv_path.resolve()),
            "-threads",
            str(threads),
        ]

        if use_2d:
            cmd.append("-2d")
        if use_3d:
            cmd.append("-3d")
        if use_fp:
            cmd.append("-fingerprints")
        if remove_salts:
            cmd.append("-removesalt")
        if standardize_nitro:
            cmd.append("-standardizenitro")
        if standardize_tautomers:
            cmd.append("-standardizetautomers")
        if retain_order:
            cmd.append("-retainorder")
        if use_filename_as_molname:
            cmd.append("-usefilenameasmolname")

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(temp_path),
            )
            elapsed_time = round(time.time() - start_time, 2)

            if proc.returncode != 0:
                return {
                    "success": False,
                    "csv_path": None,
                    "output_bytes": None,
                    "elapsed_time": elapsed_time,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "error": f"PaDEL process failed with exit code {proc.returncode}.\n{proc.stderr}",
                }

            if not output_csv_path.exists() or output_csv_path.stat().st_size == 0:
                return {
                    "success": False,
                    "csv_path": None,
                    "output_bytes": None,
                    "elapsed_time": elapsed_time,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "error": "PaDEL finished but did not produce a non-empty results CSV file. Please check input molecule structures.",
                }

            # Read result bytes while temp dir is open
            output_bytes = output_csv_path.read_bytes()

            return {
                "success": True,
                "csv_path": str(output_csv_path),
                "output_bytes": output_bytes,
                "elapsed_time": elapsed_time,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "csv_path": None,
                "output_bytes": None,
                "elapsed_time": round(time.time() - start_time, 2),
                "stdout": "",
                "stderr": "",
                "error": f"PaDEL calculation timed out after {timeout_sec} seconds.",
            }
        except Exception as e:
            return {
                "success": False,
                "csv_path": None,
                "output_bytes": None,
                "elapsed_time": round(time.time() - start_time, 2),
                "stdout": "",
                "stderr": "",
                "error": f"Unexpected execution error: {str(e)}",
            }
