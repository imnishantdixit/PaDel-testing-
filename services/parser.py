"""
CSV Result Parser & Metrics Generator Service for PaDEL-Descriptor.
Parses output CSV data, handles molecule naming, counts descriptors vs fingerprints,
and provides dynamic category classification, preset filtering, and search capabilities.
"""

import io
from typing import Tuple, Dict, Any, List, Optional
import pandas as pd


FINGERPRINT_KEYWORDS = (
    "pubchemfp",
    "subfp",
    "klekotarothfp",
    "maccsfp",
    "estatefp",
    "cdkfp",
    "subfpc",
    "atompairs2dfp",
    "fingerprint",
)


def clean_molecule_names(df: pd.DataFrame, custom_names: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Improves molecule naming in the DataFrame while preserving original descriptor columns.
    
    Rules:
    - If a row name is 'AUTOGEN_molecules', blank, or missing, replace with custom name or Molecule_001.
    - If names are provided in uploaded file/SMILES, preserve them.
    - Never modify underlying numeric descriptor values or original column names.
    """
    if df is None or df.empty or "Name" not in df.columns:
        return df

    cleaned_df = df.copy()
    names = list(cleaned_df["Name"])
    new_names = []

    for i, current_name in enumerate(names):
        curr_str = str(current_name).strip() if pd.notna(current_name) else ""
        if not curr_str or "AUTOGEN" in curr_str.upper():
            if custom_names and i < len(custom_names) and custom_names[i].strip():
                new_names.append(custom_names[i].strip())
            else:
                new_names.append(f"Molecule_{i+1:03d}")
        else:
            new_names.append(curr_str)

    cleaned_df["Name"] = new_names
    return cleaned_df


def count_descriptors_and_fingerprints(df: pd.DataFrame) -> Tuple[int, int]:
    """
    Distinguishes molecular descriptor columns from fingerprint columns dynamically.

    Returns:
        (descriptor_count, fingerprint_count)
    """
    if df is None or df.empty:
        return 0, 0

    cols = [c for c in df.columns if c != "Name"]
    fp_count = 0
    desc_count = 0

    for c in cols:
        c_lower = c.lower()
        if any(keyword in c_lower for keyword in FINGERPRINT_KEYWORDS):
            fp_count += 1
        else:
            desc_count += 1

    return desc_count, fp_count


def get_descriptor_categories(all_columns: List[str]) -> Dict[str, List[str]]:
    """
    Dynamically maps actual DataFrame column names into logical scientific categories.
    Only categories containing at least 1 matching column are included.
    """
    cols = [c for c in all_columns if c != "Name"]

    # Category definitions with keywords
    cat_definitions = {
        "Lipophilicity & LogP": ["logp", "alogp", "crippen", "mlogp", "xlogp"],
        "Molecular Weight & Size": ["mw", "amw", "natom", "nheavyatom", "nc", "no", "nn", "nf", "np", "ns", "ncl", "nbr", "ni", "nb", "nh"],
        "Hydrogen Bonding": ["hbacc", "hbdon", "nhbacc", "nhbdon"],
        "Aromaticity & Rings": ["ring", "aromatic", "arom", "nring", "naring", "narombond", "naaromatom"],
        "Surface Area & Charge": ["tpsa", "charge", "topochemical", "cpsa", "apol", "bpol", "peoe"],
        "Topological": ["zagreb", "wiener", "petitjean", "balaban", "bertz", "chi", "kier", "bcut", "estate"],
        "3D Descriptors": ["rdf", "3dmorse", "whim", "getaway", "eigenvalue", "geometrical", "gravitational"],
        "Fingerprints": list(FINGERPRINT_KEYWORDS),
    }

    categorized: Dict[str, List[str]] = {"All Columns": list(all_columns)}

    for cat_name, keywords in cat_definitions.items():
        matched = []
        for col in cols:
            col_lower = col.lower()
            if any(kw in col_lower for kw in keywords):
                matched.append(col)
        if matched:
            categorized[cat_name] = matched

    # Collect any unclassified columns into 'Other Descriptors'
    all_classified = set()
    for cat_name, col_list in categorized.items():
        if cat_name != "All Columns":
            all_classified.update(col_list)

    other_cols = [c for c in cols if c not in all_classified]
    if other_cols:
        categorized["Other Descriptors"] = other_cols

    return categorized


def get_quick_presets(all_columns: List[str]) -> Dict[str, List[str]]:
    """
    Returns quick column presets populated dynamically using existing DataFrame columns.
    """
    cols_set = set(all_columns)

    def pick_existing(desired_list: List[str]) -> List[str]:
        res = ["Name"] if "Name" in cols_set else []
        for c in desired_list:
            if c in cols_set and c not in res:
                res.append(c)
        return res

    # 1. Default preview preset: Name + top 5 essential properties
    default_desired = ["ALogP", "AMR", "apol", "nAtom", "nHeavyAtom", "MW", "TPSA", "nHBAcc", "nHBDon"]
    default_cols = pick_existing(default_desired)
    if len(default_cols) <= 1:
        default_cols = list(all_columns[:6])

    # 2. Basic Properties preset
    basic_desired = ["MW", "AMW", "ALogP", "AMR", "apol", "nAtom", "nHeavyAtom", "nAcid", "nBase", "TPSA", "nHBAcc", "nHBDon"]
    basic_cols = pick_existing(basic_desired)

    # 3. Lipophilicity preset (all LogP related columns)
    lipo_cols = ["Name"] if "Name" in cols_set else []
    for c in all_columns:
        if "logp" in c.lower() or "crippen" in c.lower():
            if c not in lipo_cols:
                lipo_cols.append(c)

    # 4. Drug-Likeness preset
    drug_desired = ["MW", "ALogP", "ALogp2", "TPSA", "nHBAcc", "nHBDon", "nRotB", "AMR", "apol", "nAtom"]
    drug_cols = pick_existing(drug_desired)

    # 5. Fingerprints Overview preset
    fp_cols = ["Name"] if "Name" in cols_set else []
    for c in all_columns:
        if any(kw in c.lower() for kw in FINGERPRINT_KEYWORDS):
            fp_cols.append(c)
            if len(fp_cols) >= 16:  # Name + top 15 fingerprints
                break

    return {
        "Default Preview": default_cols,
        "Basic Properties": basic_cols if len(basic_cols) > 1 else default_cols,
        "Lipophilicity": lipo_cols if len(lipo_cols) > 1 else default_cols,
        "Drug-Likeness": drug_cols if len(drug_cols) > 1 else default_cols,
        "Fingerprints Overview": fp_cols if len(fp_cols) > 1 else default_cols,
    }


def search_descriptor_columns(all_columns: List[str], query: str) -> List[str]:
    """
    Performs case-insensitive search across column names.
    Returns list of exact matching column names.
    """
    if not query or not query.strip():
        return []

    q = query.strip().lower()
    return [c for c in all_columns if q in c.lower() and c != "Name"]


def parse_padel_csv(
    csv_bytes: bytes, custom_names: Optional[List[str]] = None
) -> Tuple[bool, Optional[pd.DataFrame], Dict[str, Any], Optional[str]]:
    """
    Parses raw CSV bytes from PaDEL execution into a Pandas DataFrame and summary metrics.

    Returns:
        (success, dataframe, summary_dict, error_message)
    """
    if not csv_bytes or len(csv_bytes) == 0:
        return False, None, {}, "CSV data is empty."

    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))

        if df.empty:
            return False, None, {}, "Parsed dataframe is empty."

        # Clean molecule names without touching descriptors or column names
        df = clean_molecule_names(df, custom_names=custom_names)

        total_molecules = len(df)
        total_columns = len(df.columns)
        desc_count, fp_count = count_descriptors_and_fingerprints(df)

        nan_counts = df.isna().sum().sum()
        name_col = df.columns[0]

        summary = {
            "molecules_count": total_molecules,
            "total_columns": total_columns,
            "descriptors_count": desc_count,
            "fingerprints_count": fp_count,
            "can_distinguish_fp": fp_count > 0 and desc_count > 0,
            "name_column": name_col,
            "has_nans": bool(nan_counts > 0),
            "total_nans": int(nan_counts),
            "columns_list": list(df.columns),
        }

        return True, df, summary, None

    except Exception as e:
        return False, None, {}, f"Error parsing CSV result: {str(e)}"


def filter_preview_dataframe(
    df: pd.DataFrame,
    selected_columns: Optional[List[str]] = None,
    molecule_search_query: str = "",
) -> pd.DataFrame:
    """
    Filters DataFrame by selected columns and molecule name search query.
    Preserves exact column names, data values, and original DataFrame.
    """
    if df is None or df.empty:
        return df

    filtered = df.copy()

    # 1. Filter rows by molecule search query
    if molecule_search_query and molecule_search_query.strip():
        q = molecule_search_query.strip().lower()
        if "Name" in filtered.columns:
            filtered = filtered[filtered["Name"].astype(str).str.lower().str.contains(q)]

    # 2. Filter columns by selected columns list
    if selected_columns and len(selected_columns) > 0:
        cols_to_keep = []
        if "Name" in df.columns and "Name" not in selected_columns:
            cols_to_keep.append("Name")
        for c in df.columns:
            if c in selected_columns and c not in cols_to_keep:
                cols_to_keep.append(c)
        filtered = filtered[cols_to_keep]

    return filtered


def export_selected_columns_csv(df: pd.DataFrame, selected_columns: List[str]) -> bytes:
    """
    Exports CSV containing only currently selected columns and filtered molecules.
    """
    filtered_df = filter_preview_dataframe(df, selected_columns=selected_columns)
    output_buf = io.BytesIO()
    filtered_df.to_csv(output_buf, index=False)
    return output_buf.getvalue()
