This project captures and visualizes wideband RF spectrum activity to analyze ExpressLRS (ELRS) transmissions under real-world conditions.

Using HackRF One and hackrf_sweep, we capture a full sweep from 750 MHz to 2700 MHz, then generate comparative spectrum plots (baseline vs active ELRS transmission) using a custom Python script.

The goal is to:

Visualize overall RF energy distribution

Highlight ELRS band activity

Detect interference or spectral footprint

Compare idle vs active transmission states

🔹 Hardware & Tools Used

HackRF One

ExpressLRS TX module

Python 3.x

hackrf_sweep utility

🔹 1️⃣ Wideband Capture (750–2700 MHz)
Baseline (ELRS OFF)
hackrf_sweep -f 750:2700 -w 2000000 -l 20 -g 6 > wide_off_750_2700_B.csv

Active Transmission (ELRS ON)
hackrf_sweep -f 750:2700 -w 2000000 -l 20 -g 6 > wide_on_750_2700_B.csv


Sweep parameters:

Frequency range: 750–2700 MHz

Resolution bandwidth: 2 MHz

LNA gain: 20

VGA gain: 6

🔹 2️⃣ Generate Comparison Plots

Single command to generate both spectrum visualizations:

python elrs_wide_plot_onecmd.py \
  --on wide_on_750_2700_B.csv \
  --off wide_off_750_2700_B.csv \
  --range 750:2700 \
  --out wide_750_2700_B

Output:

wide_750_2700_B_absolute_power.png
→ Absolute RF power comparison

wide_750_2700_B_activity_highlight.png
→ Differential activity plot (ELRS activity emphasized)

🔹 What This Shows

Full X-band + 2.4 GHz + surrounding spectrum context

ELRS transmission footprint

Real RF environment noise floor

Interference visibility under heavy wireless traffic

🔹 Use Cases

ELRS interference analysis

RF environment characterization

Spectrum footprint visualization

Educational SDR demonstrations

YouTube technical content (RF analysis / ELRS immunity testing)
