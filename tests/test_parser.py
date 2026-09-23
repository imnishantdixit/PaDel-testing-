"""
Unit tests for services/parser.py
"""

import pytest
import pandas as pd
from services.parser import (
    parse_padel_csv,
    clean_molecule_names,
    count_descriptors_and_fingerprints,
    get_descriptor_categories,
    get_quick_presets,
    search_descriptor_columns,
    filter_preview_dataframe,
    export_selected_columns_csv,
)


def test_clean_molecule_names_autogen():
    csv_str = "Name,ALogP,PubchemFP0\nAUTOGEN_molecules,0.5,1\nAUTOGEN_molecules,1.2,0\n"
    df = pd.read_csv(pd.io.common.BytesIO(csv_str.encode("utf-8")))
    cleaned = clean_molecule_names(df)
    assert list(cleaned["Name"]) == ["Molecule_001", "Molecule_002"]


def test_clean_molecule_names_custom():
    csv_str = "Name,ALogP,PubchemFP0\nAUTOGEN_molecules,0.5,1\nAUTOGEN_molecules,1.2,0\n"
    df = pd.read_csv(pd.io.common.BytesIO(csv_str.encode("utf-8")))
    cleaned = clean_molecule_names(df, custom_names=["Ethanol", "Aspirin"])
    assert list(cleaned["Name"]) == ["Ethanol", "Aspirin"]


def test_parse_padel_csv_success():
    csv_str = "Name,ALogP,MW,PubchemFP0,PubchemFP1\nMol1,-0.24,46.07,1,0\nMol2,-0.17,60.05,0,1\n"
    csv_bytes = csv_str.encode("utf-8")
    
    success, df, summary, err = parse_padel_csv(csv_bytes)
    assert success is True
    assert df is not None
    assert summary["molecules_count"] == 2
    assert summary["total_columns"] == 5
    assert summary["descriptors_count"] == 2
    assert summary["fingerprints_count"] == 2
    assert summary["can_distinguish_fp"] is True


def test_descriptor_categories_and_presets():
    cols = ["Name", "ALogP", "ALogp2", "CrippenLogP", "MW", "nAtom", "nHBAcc", "PubchemFP0"]
    categories = get_descriptor_categories(cols)
    assert "Lipophilicity & LogP" in categories
    assert "ALogP" in categories["Lipophilicity & LogP"]
    assert "Fingerprints" in categories
    assert "PubchemFP0" in categories["Fingerprints"]

    presets = get_quick_presets(cols)
    assert "Lipophilicity" in presets
    assert "ALogP" in presets["Lipophilicity"]


def test_search_descriptor_columns():
    cols = ["Name", "ALogP", "ALogp2", "CrippenLogP", "MLogP", "XLogP", "MW", "TPSA"]
    matches = search_descriptor_columns(cols, "LogP")
    assert matches == ["ALogP", "ALogp2", "CrippenLogP", "MLogP", "XLogP"]


def test_export_selected_columns_csv():
    csv_str = "Name,ALogP,MW,PubchemFP0\nEthanol,-0.1,46.0,1\nAspirin,1.2,180.1,0\n"
    success, df, summary, err = parse_padel_csv(csv_str.encode("utf-8"))
    
    selected_csv_bytes = export_selected_columns_csv(df, selected_columns=["ALogP"])
    exported_df = pd.read_csv(pd.io.common.BytesIO(selected_csv_bytes))
    assert list(exported_df.columns) == ["Name", "ALogP"]
    assert len(exported_df) == 2
