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

  # ✅ Place it outside if/else, but still inside `with st.sidebar:`
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
        
    seed_val = st.number_input(
        "Random Seed (For Reproducibility)", min_value=0, max_value=999999, value=42
    )
    run_btn = st.button("🚀 Run Optimization", type="primary")

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
        st.write(f"**Optimization complete.** Final Penalty Score: `{final_score}`")
        if final_score > 0:
            st.caption("Note: Score > 0 indicates forced neighbor collisions due to strict mathematical limits in small grid sizes.")
            
        # 2. Generate Excel bytes
        excel_data = generate_excel_bytes(trial_name, genotypes, final_grids, reps, rows, cols, start_plot, start_row, start_col)
        
        dl_name = f"{trial_name}_Field_Layout.xlsx".replace(" ", "_")
        st.download_button(
            label=f"💾 Download {trial_name} Layout", 
            data=excel_data, 
            file_name=dl_name, 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
