"""
Integration test for services/padel_runner.py with real PaDEL Java engine.
"""

import pytest
from pathlib import Path
from services.padel_runner import run_padel_calculation
from services.parser import parse_padel_csv


def test_run_padel_calculation_smiles():
    smiles = "CCO Ethanol\nCC(=O)O Acetic_Acid"
    res = run_padel_calculation(
        input_content=smiles,
        input_filename="test.smi",
        use_2d=True,
        use_3d=False,
        use_fp=False,
        threads=2,
    )
    assert res["success"] is True, f"Calculation failed: {res['error']}"
    assert res["output_bytes"] is not None
    assert res["elapsed_time"] > 0

    success, df, summary, err = parse_padel_csv(res["output_bytes"])
    assert success is True
    assert summary["molecules_count"] == 2
    assert summary["descriptors_count"] > 1
