import streamlit as st
import random
import os
import signal
from core.optimizer import run_sa_optimization
from core.fieldbook import generate_excel_bytes


st.set_page_config(page_title="Spatial Field Trial Randomizer", layout="wide")

is_cloud = (
    os.path.exists("/home/appuser")
    or os.environ.get("STREAMLIT_SERVER_GATHER_USAGE_STATS") == "false"
    and not os.name == "nt"
    or "HOSTNAME" in os.environ
    and "streamlit" in os.environ["HOSTNAME"].lower()
)

with st.sidebar:
  st.subheader("Session Control")
  if is_cloud:
    st.caption("ℹ️ Running on Streamlit Community Cloud (hosted demo).")
  else:
    st.info("Local session active.")
    if st.button("🛑 Exit", type="primary", use_container_width=True):
      os.kill(os.getpid(), signal.SIGTERM)
      
  st.markdown("---")
  st.markdown("**Developed by Sudip Kundu**")
  st.markdown("[Connect on LinkedIn](https://www.linkedin.com/in/sudip-kundu-698b43188/)")

st.title("🌾 Spatial Field Trial Randomizer")
st.markdown("This tool automates spatial field layout generation to minimize boundary and neighborhood collisions between genotypes.")

c1, c2 = st.columns([1, 2])

with c1:
    raw_input = st.text_area("Paste Genotypes (one per line):", height=300)
    genotypes = [x.strip() for x in raw_input.split('\n') if x.strip()]
    n_lines = len(genotypes)
    if n_lines > 0:
        st.success(f"Loaded {n_lines} genotypes.")

with c2:
    trial_name = st.text_input("Trial Name", placeholder="e.g. MLT or IVT-1")
    
    col_a, col_b = st.columns(2)
    with col_a:
        reps = st.number_input("Replications", min_value=1, value=3)
        tiers = st.number_input("Tiers per Rep", min_value=1, value=2)
    with col_b:
        start_plot = st.number_input("Starting Plot", min_value=1, value=1)
        start_row = st.number_input("Starting Row", min_value=1, value=1)
        start_col = st.number_input("Starting Col", min_value=1, value=1)
        
         
    st.markdown("---")
    use_trial_details = st.checkbox("Add Extended Trial Details to Excel Header")
    trial_details = None
    if use_trial_details:
        with st.container():
            c_det1, c_det2 = st.columns(2)
        with c_det1:
            # Using placeholders instead of fixed values
            crop_season = st.text_input("Crop & Season", value="", placeholder="e.g., Wheat Rabi (2026-27)")
            num_locations = st.number_input("No. of Locations", min_value=1, value=1)
            row_length = st.text_input("Row Length (m)", value="", placeholder="e.g., 4 m")
        with c_det2:
            location_name = st.text_input("Location Name", value="", placeholder="e.g., Lucknow")
            num_rows = st.number_input("No. of Rows (per plot)", min_value=1, value=1)
            area = st.text_input("Required Area (Sqmt.)", value="", placeholder="e.g., 900")
            
            include_dos = st.checkbox("Include Date of Sowing (DOS) row?")
            dos = None
            if include_dos:
                dos = st.text_input("Date of Sowing (DOS)", value="", placeholder="Leave blank to write on paper")
                
        trial_details = {
            "crop_season": crop_season,
            "num_locations": num_locations,
            "row_length": row_length,
            "location_name": location_name,
            "num_rows": num_rows,
            "area": area,
            "dos": dos,
            "n_entries": n_lines
            
        }
    st.markdown("---")
    append_to_existing = st.checkbox("Append to an existing Excel file?")
    existing_file = None
    if append_to_existing:
        existing_file = st.file_uploader("Upload Master Workbook (.xlsx)", type=["xlsx"])
        
    st.markdown("---")
    add_traits = st.checkbox("Add Custom Trait Columns for Data Collection?")
    traits_list = []
    if add_traits:
        traits_input = st.text_area(
            "Enter traits separated by commas", 
            placeholder="e.g., GERM %, P.P, DFL, PH (cm), Grain Wt (Kg)"
        )
        if traits_input.strip():
            traits_list = [x.strip() for x in traits_input.split(",") if x.strip()]
        
    seed_val = st.number_input(
        "Random Seed (For Reproducibility)", min_value=0, max_value=999999, value=42
    )
    run_btn = st.button("🚀 Generate Fieldbook", type="primary")

if run_btn:
  random.seed(seed_val)

if run_btn:
    if not trial_name.strip():
        st.error("Please enter a Trial Name.")
    elif n_lines == 0:
        st.error("No genotypes found.")
    elif n_lines % tiers != 0:
        st.error(f"Cannot split {n_lines} genotypes into {tiers} tiers evenly.")
    else:
        rows = tiers
        cols = n_lines // tiers
        
        pbar = st.progress(0)
        
        # Define callback for progress bar
        def update_progress(val):
            pbar.progress(val)

        # 1. Run Core Optimizer
        final_grids, final_score = run_sa_optimization(genotypes, reps, rows, cols, update_progress)
        
        # Save score to session state so it survives the download click
        st.session_state["final_score"] = final_score
            
        # 2. Generate Excel bytes
        excel_data = generate_excel_bytes(
            trial_name,
            genotypes,
            final_grids,
            reps,
            rows,
            cols,
            start_plot,
            start_row,
            start_col,
            trial_details=trial_details,
            existing_file=existing_file,
            traits_list=traits_list
        )
            
        # 3. Store file data and labels in Session State
        st.session_state["excel_data"] = excel_data
        
        if existing_file is not None:
            st.session_state["dl_name"] = existing_file.name
            st.session_state["btn_label"] = f"💾 Download Updated Master: {existing_file.name}"
        else:
            st.session_state["dl_name"] = f"{trial_name}_Field_Layout.xlsx".replace(" ", "_")
            st.session_state["btn_label"] = f"💾 Download {trial_name} Layout"

# 4. OUTSIDE THE RUN BLOCK: Display results and download button
if "excel_data" in st.session_state:
    st.write(f"**Optimization complete.** Final Penalty Score: `{st.session_state['final_score']}`")
    if st.session_state["final_score"] > 0:
        st.caption("Note: Score > 0 indicates forced neighbor collisions due to strict mathematical limits in small grid sizes.")
        
    st.download_button(
        label=st.session_state["btn_label"], 
        data=st.session_state["excel_data"], 
        file_name=st.session_state["dl_name"], 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )