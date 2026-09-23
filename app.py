"""
PaDEL-Descriptor Web Application — Streamlit Interface
Designed to strictly match the light scientific UI layout & design specification.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from services import (
    validate_smiles_text,
    validate_file_upload,
    run_padel_calculation,
    parse_padel_csv,
    get_descriptor_categories,
    get_quick_presets,
    search_descriptor_columns,
    filter_preview_dataframe,
    export_selected_columns_csv,
)

# Page configuration
st.set_page_config(
    page_title="PaDEL-Descriptor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS matching target light theme screenshot
st.markdown(
    """
    <style>
    /* Global Background & Typography */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Reduce Streamlit Default Top Padding */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
    }
    
    /* Main Title Styling */
    .main-title-container {
        margin-top: 0.5rem !important;
        padding-top: 0px !important;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }
    .main-title-dark {
        color: #0F172A;
    }
    .main-title-blue {
        color: #2563EB;
    }
    .main-subtitle {
        color: #64748B;
        font-size: 1.05rem;
        font-weight: 500;
    }

    /* Section Cards (White Containers) */
    .section-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }
    .badge-number {
        background-color: #2563EB;
        color: #FFFFFF;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 15px;
        flex-shrink: 0;
    }
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0F172A;
    }
    .section-desc {
        color: #64748B;
        font-size: 0.95rem;
        margin-left: 44px;
        margin-bottom: 1.2rem;
    }

    /* Option Cards */
    .option-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        transition: all 0.2s ease;
        height: 100%;
    }
    .option-box-active {
        background-color: #EFF6FF;
        border: 1.5px solid #2563EB;
    }
    .option-box-title {
        font-weight: 700;
        color: #0F172A;
        font-size: 1.05rem;
        margin-bottom: 4px;
    }
    .option-box-desc {
        color: #64748B;
        font-size: 0.85rem;
        line-height: 1.3;
    }

    /* Sidebar Navigation Pills */
    .nav-item {
        padding: 10px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-item-active {
        background-color: #EFF6FF;
        color: #1D4ED8;
    }
    
    /* Result Metric Badges */
    .metric-card-light {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .metric-card-title {
        color: #64748B;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card-val {
        color: #0F172A;
        font-size: 1.7rem;
        font-weight: 800;
        margin-top: 2px;
    }

    /* Callout Note */
    .info-callout-light {
        background-color: #EFF6FF;
        border-left: 4px solid #2563EB;
        padding: 0.9rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1.2rem;
        font-size: 0.9rem;
        color: #1E40AF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar (Left Navigation & Branding matching target UI)
with st.sidebar:
    # Branding
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="18" cy="5" r="3"></circle>
                <circle cx="6" cy="12" r="3"></circle>
                <circle cx="18" cy="19" r="3"></circle>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
            <div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #0F172A; line-height: 1;">PaDEL</div>
                <div style="font-size: 0.75rem; color: #64748B;">PaDEL-Descriptor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="font-size: 0.85rem; color: #64748B; margin-bottom: 1.2rem;">PaDEL-Descriptor is a scientific software toolkit for calculating molecular descriptors and fingerprints.</div>',
        unsafe_allow_html=True,
    )



    st.divider()

    # Supported Descriptors
    st.markdown('<div style="font-size: 0.85rem; font-weight: 700; color: #475569; margin-bottom: 8px;">Supported Descriptors</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 10px;">
            <b>• 1D & 2D Descriptors</b><br>
            Constitutional, topological, electrotopological, autocorrelation, etc.
        </div>
        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 10px;">
            <b>• 3D Descriptors</b><br>
            Geometrical, CPSA, RDF, 3D-MoRSE, WHIM, GETAWAY, etc.
        </div>
        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
            <b>• Fingerprints</b><br>
            CDK, PubChem, Substructure, Klekota-Roth, MACCS, Estate, etc.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Status Card at Bottom of Sidebar
    st.markdown(
        """
        <div style="background-color: #EFF6FF; border-radius: 10px; padding: 12px; border: 1px solid #DBEAFE;">
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; color: #1E40AF;">
                <span style="height: 8px; width: 8px; background-color: #22C55E; border-radius: 50%; display: inline-block;"></span>
                Engine Status
            </div>
            <div style="font-size: 0.8rem; color: #475569; margin-left: 16px; margin-top: 2px;">Java 21 JRE Detected</div>
            <div style="margin-top: 8px; font-size: 0.8rem; color: #64748B;">
                <b>Version:</b> 2.2.1
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Main Title Header
st.markdown(
    """
    <div class="main-title-container">
        <div class="main-title">
            <span class="main-title-dark">PaDEL</span><span class="main-title-blue">-Descriptor</span>
        </div>
        <div class="main-subtitle">Compute 1D, 2D, 3D Molecular Descriptors & Fingerprints using PaDEL Java Engine</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. Section 1: Input Molecules Card
st.markdown(
    """
    <div class="section-header">
        <div class="badge-number">1</div>
        <div class="section-title">Input Molecules</div>
    </div>
    <div class="section-desc">Add SMILES text or upload a molecule file (.smi, .sdf, .mol, .mdl, .txt)</div>
    """,
    unsafe_allow_html=True,
)

input_tab1, input_tab2 = st.tabs(["SMILES Text Input", "Upload Molecule File"])

input_content = None
input_filename = "molecules.smi"
is_valid_input = False
validation_msg = ""
estimated_mol_count = 0
custom_molecule_names = []

with input_tab1:
    col_smiles_top, col_sample_btn = st.columns([3, 1])
    with col_sample_btn:
        if st.button("Load Sample SMILES", key="btn_sample"):
            sample_path = Path(__file__).parent / "data" / "samples" / "sample.smi"
            if sample_path.exists():
                st.session_state["smiles_input_val"] = sample_path.read_text(encoding="utf-8")

    smiles_val = st.session_state.get(
        "smiles_input_val",
        "CCO\nC1=CC=CC=C1\nCC(=O)ON",
    )

    smiles_text = st.text_area(
        "Enter SMILES strings (one per line or comma separated). Example: CCO",
        value=smiles_val,
        height=140,
        help="Example: CCO Ethanol",
    )

    if smiles_text and smiles_text.strip():
        is_valid, msg, mol_count, lines, extracted_names = validate_smiles_text(smiles_text)
        if is_valid:
            input_content = smiles_text
            input_filename = "molecules.smi"
            is_valid_input = True
            validation_msg = msg
            estimated_mol_count = mol_count
            custom_molecule_names = extracted_names
            st.caption(msg)
        else:
            st.warning(msg)

with input_tab2:
    uploaded_file = st.file_uploader(
        "Upload File (Supported formats: .smi, .sdf, .mol, .mdl, .txt)",
        type=["smi", "sdf", "mol", "mdl", "txt"],
        help="Drag and drop your file here",
    )

    if uploaded_file is not None:
        is_valid, msg, mol_count, extracted_names = validate_file_upload(uploaded_file)
        if is_valid:
            input_content = uploaded_file.getvalue()
            input_filename = uploaded_file.name
            is_valid_input = True
            validation_msg = msg
            estimated_mol_count = mol_count
            custom_molecule_names = extracted_names
            st.caption(msg)
        else:
            st.error(msg)

st.divider()

# 2. Section 2: Calculation Options Card
st.markdown(
    """
    <div class="section-header">
        <div class="badge-number">2</div>
        <div class="section-title">Calculation Options</div>
    </div>
    <div class="section-desc">Choose the type of descriptors and fingerprints you want to calculate.</div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    use_2d = st.checkbox("2D Descriptors", value=True, help="Topological, constitutional, and 2D molecular descriptors.")
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #64748B; margin-top: -10px; margin-left: 24px; margin-bottom: 12px;">
            Topological, constitutional, and 2D molecular descriptors.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    use_3d = st.checkbox("3D Descriptors", value=False, help="3D geometry and conformational descriptors.")
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #64748B; margin-top: -10px; margin-left: 24px; margin-bottom: 12px;">
            3D geometry and conformational descriptors.
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    use_fp = st.checkbox("Fingerprints", value=True, help="Molecular fingerprints (e.g., MACCS, ECFP, etc.).")
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #64748B; margin-top: -10px; margin-left: 24px; margin-bottom: 12px;">
            Molecular fingerprints (e.g., MACCS, ECFP, etc.).
        </div>
        """,
        unsafe_allow_html=True,
    )

# Advanced Parameters Expander
with st.expander("Advanced Parameters"):
    adv_col1, adv_col2 = st.columns(2)

    with adv_col1:
        st.markdown("**Processing Controls**")
        threads = st.number_input(
            "CPU Threads",
            min_value=1,
            max_value=64,
            value=4,
            help="Maximum number of parallel CPU threads to use (-threads)",
        )
        heap_str = st.selectbox(
            "Java Heap Memory Limit",
            options=["1 GB", "2 GB", "4 GB", "8 GB"],
            index=1,
            help="Maximum RAM allocated to JVM (-Xmx)",
        )
        memory_gb = int(heap_str.split()[0])

    with adv_col2:
        st.markdown("**Structure Cleaning & Output Options**")
        remove_salts = st.checkbox("Remove Salts", value=False, help="Remove salts from structures (-removesalt)")
        standardize_nitro = st.checkbox(
            "Standardize Nitro Groups", value=False, help="Standardize nitro groups to N(:O):O (-standardizenitro)"
        )
        standardize_tautomers = st.checkbox(
            "Standardize Tautomers", value=False, help="Standardize tautomers (-standardizetautomers)"
        )
        retain_order = st.checkbox(
            "Retain Input Order", value=True, help="Retain original molecule ordering in output CSV (-retainorder)"
        )
        use_filename_as_molname = st.checkbox(
            "Use Filename as Molecule Name",
            value=False,
            help="Use filename minus extension as molecule name (-usefilenameasmolname)",
        )

# Centered Run Button
st.markdown("<br>", unsafe_allow_html=True)
run_btn_col1, run_btn_col2, run_btn_col3 = st.columns([1, 2, 1])

with run_btn_col2:
    run_button = st.button("Run PaDEL", type="primary", use_container_width=True)

if run_button:
    if not is_valid_input or input_content is None:
        st.warning("Please provide valid SMILES input or upload a molecular file before running.")
    elif not (use_2d or use_3d or use_fp):
        st.warning("Please select at least one calculation option (2D Descriptors, 3D Descriptors, or Fingerprints).")
    else:
        with st.spinner("Calculating descriptors & fingerprints... Please wait."):
            res = run_padel_calculation(
                input_content=input_content,
                input_filename=input_filename,
                use_2d=use_2d,
                use_3d=use_3d,
                use_fp=use_fp,
                threads=int(threads),
                memory_gb=memory_gb,
                remove_salts=remove_salts,
                standardize_nitro=standardize_nitro,
                standardize_tautomers=standardize_tautomers,
                retain_order=retain_order,
                use_filename_as_molname=use_filename_as_molname,
            )

        if not res["success"]:
            st.error(f"Calculation Error: {res['error']}")
            if res.get("stderr") or res.get("stdout"):
                with st.expander("Technical Details"):
                    if res.get("stdout"):
                        st.code(res["stdout"], language="text")
                    if res.get("stderr"):
                        st.code(res["stderr"], language="text")
        else:
            st.success(f"Calculation completed successfully in {res['elapsed_time']} seconds.")

            # Parse results and apply clean molecule names
            parse_success, df, summary, parse_err = parse_padel_csv(
                res["output_bytes"], custom_names=custom_molecule_names
            )
            if parse_success:
                st.session_state["results_df"] = df
                st.session_state["results_summary"] = summary
                st.session_state["results_bytes"] = res["output_bytes"]
                st.session_state["elapsed_time"] = res["elapsed_time"]
            else:
                st.error(f"Error parsing generated CSV: {parse_err}")

# Section 3: Results Section
if "results_df" not in st.session_state or st.session_state["results_df"] is None:
    st.info("No results yet. Upload a molecule file or enter SMILES above and click 'Run PaDEL'.")
else:
    df = st.session_state["results_df"]
    summary = st.session_state["results_summary"]
    output_bytes = st.session_state["results_bytes"]
    elapsed_time = st.session_state["elapsed_time"]
    all_columns = summary["columns_list"]

    st.divider()

    # Section 3 Badge Header
    st.markdown(
        """
        <div class="section-header">
            <div class="badge-number">3</div>
            <div class="section-title">Results Summary</div>
        </div>
        <div class="section-desc">View computed descriptors, explore categories, and download full CSV dataset.</div>
        """,
        unsafe_allow_html=True,
    )

    # Clean Metric Cards (Light Mode)
    if summary.get("can_distinguish_fp", False):
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Molecules</div><div class="metric-card-val">{summary["molecules_count"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Descriptors</div><div class="metric-card-val">{summary["descriptors_count"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Fingerprints</div><div class="metric-card-val">{summary["fingerprints_count"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Processing Time</div><div class="metric-card-val">{elapsed_time:.2f} s</div></div>',
                unsafe_allow_html=True,
            )
    else:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Molecules Processed</div><div class="metric-card-val">{summary["molecules_count"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Output Columns</div><div class="metric-card-val">{summary["total_columns"]}</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="metric-card-light"><div class="metric-card-title">Processing Time</div><div class="metric-card-val">{elapsed_time:.2f} s</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("Descriptor Explorer")

    # Dynamic Categories & Presets
    categories_dict = get_descriptor_categories(all_columns)
    presets_dict = get_quick_presets(all_columns)

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1.5, 1.5, 1])

    with ctrl_col1:
        search_query = st.text_input("Search descriptors", placeholder="e.g. LogP, MW, TPSA, PubChem", key="desc_search")

    with ctrl_col2:
        selected_category = st.selectbox(
            "Category",
            options=list(categories_dict.keys()),
            index=0,
            help="Filter descriptors by scientific domain",
        )

    with ctrl_col3:
        selected_preset = st.selectbox(
            "Quick Preset",
            options=list(presets_dict.keys()),
            index=0,
            help="Quickly load pre-defined descriptor subsets",
        )

    with ctrl_col4:
        rows_limit = st.selectbox("Rows", options=[10, 25, 50, 100, "All"], index=0)

    # Informational Tooltip / Callout for LogP descriptors
    has_logp_in_search = "logp" in search_query.lower() if search_query else False
    if has_logp_in_search or selected_category == "Lipophilicity & LogP" or selected_preset == "Lipophilicity":
        st.markdown(
            '<div class="info-callout-light"><b>LogP Descriptors Note:</b> PaDEL provides multiple LogP implementations (e.g. <i>ALogP, ALogp2, CrippenLogP, MLogP, XLogP</i>). These represent distinct theoretical models and should be evaluated individually rather than merged.</div>',
            unsafe_allow_html=True,
        )

    # Handle Search & Selection Logic
    active_selected_cols = []

    # Priority 1: Preset selection base
    preset_cols = presets_dict.get(selected_preset, [])

    # Priority 2: Category filter
    category_cols = categories_dict.get(selected_category, all_columns)

    # Priority 3: Explicit search query matching
    matched_search_cols = search_descriptor_columns(all_columns, search_query) if search_query.strip() else []

    if search_query.strip():
        if matched_search_cols:
            st.markdown(f"**Matching Descriptors for '{search_query.strip()}'** ({len(matched_search_cols)} found):")
            chosen_searched = st.multiselect(
                "Select matching descriptors to display:",
                options=matched_search_cols,
                default=matched_search_cols[: min(10, len(matched_search_cols))],
                key="searched_multiselect",
            )
            active_selected_cols = chosen_searched
        else:
            st.info(f"No descriptors found matching '{search_query.strip()}'.")
            active_selected_cols = []
    elif selected_category != "All Columns":
        active_selected_cols = category_cols
    else:
        active_selected_cols = preset_cols

    # Additional Manual Column Picker
    with st.expander("Custom Column Selector (Add/Remove specific columns)"):
        user_custom_cols = st.multiselect(
            "Select specific columns to inspect:",
            options=[c for c in all_columns if c != "Name"],
            default=[c for c in active_selected_cols if c != "Name"],
            key="custom_col_multiselect",
        )
        if user_custom_cols:
            active_selected_cols = user_custom_cols

    # Molecule Search Row Filter
    col_mol_search, _ = st.columns([2, 2])
    with col_mol_search:
        mol_search_query = st.text_input("Search molecules by name", placeholder="e.g. Ethanol, Molecule_001")

    # Apply filters to preview DataFrame
    filtered_df = filter_preview_dataframe(
        df,
        selected_columns=active_selected_cols,
        molecule_search_query=mol_search_query,
    )

    if filtered_df.empty:
        if mol_search_query and mol_search_query.strip():
            st.warning(f"No molecules match your search query '{mol_search_query}'.")
        else:
            st.warning("No descriptors selected or available to display.")
    else:
        # Apply row limits
        if rows_limit != "All":
            display_df = filtered_df.head(int(rows_limit))
        else:
            display_df = filtered_df

        # Display Data Table
        st.dataframe(display_df, use_container_width=True)

        # Dynamic Column & Row Count Information
        shown_cols_count = len(filtered_df.columns) - (1 if "Name" in filtered_df.columns else 0)
        total_avail_cols = len(all_columns) - (1 if "Name" in all_columns else 0)

        st.caption(
            f"Showing **{len(display_df)} of {len(df)}** molecules | Showing **{shown_cols_count} of {total_avail_cols}** available descriptor columns"
        )

    # Dual CSV Download Buttons
    st.divider()
    col_dn1, col_dn2 = st.columns(2)

    with col_dn1:
        st.download_button(
            label=f"Download Complete CSV (All {len(all_columns)} Columns)",
            data=output_bytes,
            file_name="descriptors_complete.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
            help="Download complete raw original PaDEL CSV containing all 2326 output columns",
        )

    with col_dn2:
        selected_csv_bytes = export_selected_columns_csv(df, selected_columns=active_selected_cols)
        st.download_button(
            label=f"Download Selected Columns CSV ({len(active_selected_cols)} Columns)",
            data=selected_csv_bytes,
            file_name="descriptors_selected.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download CSV containing only the currently selected preview columns and filtered molecules",
        )
