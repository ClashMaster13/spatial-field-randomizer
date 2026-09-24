# Spatial Field Trial Randomizer

A local web application and global optimization engine that generates spatially balanced multi-tier field layouts for crop breeding trials. 

## The Agronomic Problem
Standard Randomized Complete Block Designs (RCBD) often fail to account for physical field boundaries when plots are stacked into multiple tiers. In small-plot breeding trials, simple randomization can unintentionally cluster identical genotypes across replications or force severe boundary edge-effects.

This tool utilizes a **Simulated Annealing algorithm** to globally minimize spatial confounding across all replications simultaneously.

## Objective Function
The optimizer evaluates up to 200,000 Markov Chain Monte Carlo (MCMC) state transitions, penalizing layouts based on the following constraints:

$$\min \sum \left( w_{col} C_{col} + w_{alley} C_{alley} + w_{nbr} C_{nbr} + w_{border} C_{border} \right)$$

1. **Strict Column Isolation:** Prevents the same genotype from reappearing in the exact same vertical column across all replications.
2. **Alley Boundary Contact:** Evaluates inter-replication vertical and diagonal adjacency to prevent plots from touching across field alleyways.
3. **8-Neighborhood Dispersal:** Ensures pairwise genotype associations (Genotype A next to Genotype B) are thoroughly randomized and penalized if repeated globally.
4. **Lateral Border Balancing:** Restricts any single genotype from appearing on the true outer lateral edges (Col 1 or Col N) more than once, mitigating harsh environmental perimeter effects.

## Features
* **Streamlit Interface:** Clean, user-friendly UI designed for researchers to deploy locally without touching code.
* **Deterministic Generation:** Fixed random seeds ensure reproducible layouts.
* **Color-Coded Output:** Automatically maps genotypes to a high-contrast pastel palette, generating a print-ready `openpyxl` field map and data collection fieldbook.

## Installation & Usage
1. Clone the repository:
   ```bash
   git clone [https://github.com/ClashMaster13/spatial-field-randomizer.git](https://github.com/ClashMaster13/spatial-field-randomizer.git)
   ```
   
2. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
3. Run the application:
   - **One-click (Windows):** Double-click `Launch_Script.bat`
   - **Command Line:**
     ```cmd
     Launch_Script.bat
     ```
   - **Manual Streamlit:**
     ```bash
     streamlit run app.py
     ```