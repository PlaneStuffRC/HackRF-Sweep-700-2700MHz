# 📡 ELRS Wideband Spectrum Analysis (750–2700 MHz)

![Python](https://img.shields.io/badge/Python-3.x-blue)
![HackRF](https://img.shields.io/badge/Hardware-HackRF%20One-orange)
![License](https://img.shields.io/badge/License-MIT-green)

Wideband RF spectrum capture and comparison of ExpressLRS (ELRS) activity using HackRF One and Python.

This project captures a full sweep from **750 MHz to 2700 MHz**, compares baseline vs active ELRS transmission, and generates visual spectrum plots to highlight RF activity and transmission footprint.

---

## 🎯 Project Objective

- Capture wideband RF spectrum (750–2700 MHz)
- Compare baseline vs active ELRS transmission
- Visualize spectrum occupancy
- Highlight transmission activity
- Analyze interference behavior under real-world RF conditions

---

## 🛠 Hardware & Software Requirements

### Hardware
- HackRF One (SDR device)
- ExpressLRS transmitter module
- Suitable RF antenna

### Software
- Python 3.x
- hackrf_sweep utility (part of HackRF tools)
- Required Python packages (see below)

---
Nice to read
https://skylinedrones.ro/drone-jamming-in-eastern-europe/
https://www.nccgroup.com/research-blog/technical-advisory-expresslrs-vulnerabilities-allow-for-hijack-of-control-link/
https://events.gnuradio.org/event/26/contributions/771/attachments/238/622/GabrielGarcia-FAUCAAI-Grcon25.pdf

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/PlaneStuffRC/HackRF-Sweep-700-2700MHz
cd HackRF-Sweep-700-2700MHz

