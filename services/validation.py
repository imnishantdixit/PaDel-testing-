"""
Validation Service for PaDEL-Descriptor Streamlit Web Application.
Handles SMILES input strings and molecular uploaded file validation.
"""

from typing import Tuple, List, Optional
import io


ALLOWED_EXTENSIONS = {".smi", ".sdf", ".mol", ".mdl", ".txt"}
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB limit


def validate_smiles_text(smiles_text: str) -> Tuple[bool, str, int, List[str], List[str]]:
    """
    Validates user-pasted multiline SMILES text and extracts custom molecule names if present.

    Returns:
        (is_valid, message, molecule_count, parsed_lines, extracted_names)
    """
    if not smiles_text or not smiles_text.strip():
        return False, "SMILES input is empty. Please enter one or more SMILES strings.", 0, [], []

    lines = [line.strip() for line in smiles_text.strip().splitlines() if line.strip()]
    if not lines:
        return False, "No valid SMILES lines found.", 0, [], []

    valid_count = 0
    clean_lines = []
    extracted_names = []

    for idx, line in enumerate(lines):
        tokens = line.split(maxsplit=1)
        if len(tokens) > 0 and len(tokens[0]) > 0:
            clean_lines.append(line)
            valid_count += 1
            if len(tokens) > 1 and tokens[1].strip():
                extracted_names.append(tokens[1].strip())
            else:
                extracted_names.append(f"Molecule_{idx+1:03d}")

    if valid_count == 0:
        return False, "Could not extract any valid SMILES tokens.", 0, [], []

    return True, f"Valid SMILES input with {valid_count} molecule(s).", valid_count, clean_lines, extracted_names


def validate_file_upload(uploaded_file) -> Tuple[bool, str, int, List[str]]:
    """
    Validates an uploaded Streamlit file buffer and attempts to extract molecule names if present.

    Returns:
        (is_valid, message, molecule_count_estimate, extracted_names)
    """
    if uploaded_file is None:
        return False, "No file uploaded.", 0, []

    filename = uploaded_file.name
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"Unsupported file type '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
            0,
            [],
        )

    file_size = uploaded_file.size
    if file_size == 0:
        return False, f"Uploaded file '{filename}' is empty.", 0, []

    if file_size > MAX_FILE_SIZE_BYTES:
        return (
            False,
            f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum limit of 200 MB.",
            0,
            [],
        )

    extracted_names = []

    try:
        content_bytes = uploaded_file.getvalue()
        content_str = content_bytes.decode("utf-8", errors="ignore")

        if ext in {".smi", ".txt"}:
            lines = [l.strip() for l in content_str.splitlines() if l.strip()]
            mol_count = len(lines)
            for idx, l in enumerate(lines):
                tokens = l.split(maxsplit=1)
                if len(tokens) > 1 and tokens[1].strip():
                    extracted_names.append(tokens[1].strip())
                else:
                    extracted_names.append(f"Molecule_{idx+1:03d}")

        elif ext in {".sdf", ".mol", ".mdl"}:
            # Standard SDF format: First line of each compound block is compound name
            blocks = content_str.split("$$$$")
            clean_blocks = [b.strip() for b in blocks if b.strip()]
            mol_count = len(clean_blocks)
            for idx, block in enumerate(clean_blocks):
                first_line = block.splitlines()[0].strip() if block.splitlines() else ""
                if first_line and not first_line.startswith(">"):
                    extracted_names.append(first_line)
                else:
                    extracted_names.append(f"Molecule_{idx+1:03d}")
        else:
            mol_count = 1
            extracted_names.append("Molecule_001")

        return True, f"File '{filename}' validated ({mol_count} estimated molecule(s)).", mol_count, extracted_names
    except Exception as e:
        return False, f"Error reading file '{filename}': {str(e)}", 0, []
