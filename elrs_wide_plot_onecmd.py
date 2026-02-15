#!/usr/bin/env python3
import re
import argparse
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

LINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2},\s*\d{2}:\d{2}:\d{2}")

def parse_hackrf_sweep(path: str):
    """Parse hackrf_sweep rtl_power-like CSV lines into (times, freqs_hz, pwr[T,F])."""
    segments_by_time = defaultdict(list)
    all_freqs = set()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or not LINE_RE.match(line):
                continue  # skip debug/status lines

            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 7:
                continue

            ts = f"{parts[0]} {parts[1]}"

            try:
                hz_low = float(parts[2])
                hz_high = float(parts[3])
                bin_hz = float(parts[4])
            except ValueError:
                continue

            try:
                pvals = np.array([float(x) for x in parts[6:]], dtype=np.float32)
            except ValueError:
                continue

            if bin_hz <= 0 or pvals.size == 0:
                continue

            idx = np.arange(pvals.size, dtype=np.float64)
            f_centers = hz_low + (idx + 0.5) * bin_hz

            # keep bins inside segment with small tolerance
            m = (f_centers >= hz_low - bin_hz) & (f_centers <= hz_high + bin_hz)
            f_centers = f_centers[m]
            pvals = pvals[m]

            all_freqs.update(f_centers.tolist())
            segments_by_time[ts].append((f_centers, pvals))

    if not segments_by_time:
        raise RuntimeError(f"No valid hackrf_sweep CSV lines found in {path}")

    times = sorted(segments_by_time.keys())
    freqs = np.array(sorted(all_freqs), dtype=np.float64)

    f_index = {f: i for i, f in enumerate(freqs)}
    pwr = np.full((len(times), len(freqs)), np.nan, dtype=np.float32)

    for ti, ts in enumerate(times):
        for f_centers, pvals in segments_by_time[ts]:
            for f_c, p in zip(f_centers.tolist(), pvals.tolist()):
                j = f_index.get(f_c)
                if j is not None:
                    pwr[ti, j] = p

    return times, freqs, pwr

def fill_nans_col_median(pwr: np.ndarray) -> np.ndarray:
    p = pwr.copy()
    col_med = np.nanmedian(p, axis=0)
    inds = np.where(np.isnan(p))
    if inds[0].size:
        p[inds] = np.take(col_med, inds[1])
    return p

def row_normalize_median(pwr: np.ndarray) -> np.ndarray:
    row_med = np.nanmedian(pwr, axis=1, keepdims=True)
    return pwr - row_med

def crop(freq_mhz: np.ndarray, pwr: np.ndarray, fmin: float, fmax: float):
    m = (freq_mhz >= fmin) & (freq_mhz <= fmax)
    return freq_mhz[m], pwr[:, m]

def add_band_highlight(ax_top, ax_wf, f0, f1, label, alpha=0.22):
    ax_top.axvspan(f0, f1, alpha=alpha)
    ax_wf.axvspan(f0, f1, alpha=alpha)
    y_top = ax_top.get_ylim()[1]
    ax_top.text(
        (f0 + f1) / 2.0, y_top, label,
        ha="center", va="top", fontsize=11,
        bbox=dict(facecolor="black", edgecolor="#666666", alpha=0.7, pad=2)
    )

def plot_aaronia_like(
    freqs_mhz: np.ndarray,
    pwr: np.ndarray,
    out_png: str,
    title: str,
    ylabel: str,
    vmin: float,
    vmax: float,
    normalize_waterfall: bool,
    trace_ymin: float | None,
    trace_ymax: float | None,
):
    # traces
    current = pwr[-1, :]
    avg = np.mean(pwr, axis=0)
    maxhold = np.max(pwr, axis=0)

    wf = pwr.copy()
    if normalize_waterfall:
        wf = row_normalize_median(wf)

    # style
    plt.rcParams.update({
        "figure.facecolor": "black",
        "axes.facecolor": "black",
        "axes.edgecolor": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "grid.color": "#444444",
        "font.size": 10,
    })

    fig = plt.figure(figsize=(18, 7), dpi=180)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.2], hspace=0.08)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)

    ax1.plot(freqs_mhz, avg, linewidth=1.0, label="Average")
    ax1.plot(freqs_mhz, maxhold, linewidth=1.0, label="Max Hold")
    ax1.plot(freqs_mhz, current, linewidth=1.0, label="Current")

    ax1.set_xlim(float(freqs_mhz[0]), float(freqs_mhz[-1]))
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    ax1.grid(True, which="both", alpha=0.6)

    if trace_ymin is not None and trace_ymax is not None:
        ax1.set_ylim(trace_ymin, trace_ymax)
    else:
        y_lo = float(min(avg.min(), current.min())) - 5.0
        y_hi = float(max(maxhold.max(), current.max())) + 5.0
        ax1.set_ylim(y_lo, y_hi)

    leg = ax1.legend(loc="upper right", framealpha=0.2)
    for t in leg.get_texts():
        t.set_color("white")

    extent = [float(freqs_mhz[0]), float(freqs_mhz[-1]), 0, wf.shape[0]]
    im = ax2.imshow(
        wf, aspect="auto", origin="lower", extent=extent,
        vmin=vmin, vmax=vmax, interpolation="nearest", cmap="inferno"
    )
    ax2.set_xlabel("Frequency (MHz)")
    ax2.set_ylabel("Time (index)")

    # highlight bands
    add_band_highlight(ax1, ax2, 902.0, 928.0, "ELRS 915 (902–928 MHz)")
    add_band_highlight(ax1, ax2, 2400.0, 2485.0, "2.4 GHz (2400–2485 MHz)")

    cbar = fig.colorbar(im, ax=[ax1, ax2], fraction=0.025, pad=0.02)
    cbar.set_label("Relative Power (dB)" if normalize_waterfall else "Power (dB)")

    plt.tight_layout()
    plt.savefig(out_png, facecolor="black")
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser(
        description="ONE command -> generates BOTH: Absolute Power (ON) and Activity Highlight (Δ vs OFF) plots."
    )
    ap.add_argument("--on", required=True, help="ON capture CSV (e.g., wide_on_750_2700_B.csv)")
    ap.add_argument("--off", required=True, help="OFF baseline CSV (e.g., wide_off_750_2700_B.csv)")
    ap.add_argument("--range", default="750:2700", help="MHz range, default 750:2700")
    ap.add_argument("--out", default="wide", help="Output prefix, default 'wide' -> wide_absolute_power.png, wide_activity_highlight.png")

    # Defaults tuned for your use:
    ap.add_argument("--abs_vmin", type=float, default=-90.0)
    ap.add_argument("--abs_vmax", type=float, default=-20.0)
    ap.add_argument("--hl_vmin", type=float, default=-5.0)
    ap.add_argument("--hl_vmax", type=float, default=20.0)

    ap.add_argument("--abs_trace_ymin", type=float, default=None)
    ap.add_argument("--abs_trace_ymax", type=float, default=None)
    ap.add_argument("--hl_trace_ymin", type=float, default=None)
    ap.add_argument("--hl_trace_ymax", type=float, default=None)

    args = ap.parse_args()

    fmin, fmax = [float(x) for x in args.range.split(":")]

    # Load ON
    _, freqs_hz_on, pwr_on = parse_hackrf_sweep(args.on)
    f_mhz_on = freqs_hz_on / 1e6
    f_mhz_on, pwr_on = crop(f_mhz_on, pwr_on, fmin, fmax)
    pwr_on = fill_nans_col_median(pwr_on)

    # Load OFF
    _, freqs_hz_off, pwr_off = parse_hackrf_sweep(args.off)
    f_mhz_off = freqs_hz_off / 1e6
    f_mhz_off, pwr_off = crop(f_mhz_off, pwr_off, fmin, fmax)
    pwr_off = fill_nans_col_median(pwr_off)

    # Align OFF average onto ON axis (interpolate if needed)
    off_avg_raw = np.mean(pwr_off, axis=0)
    if f_mhz_off.size != f_mhz_on.size or np.max(np.abs(f_mhz_off - f_mhz_on)) > 1e-6:
        off_avg = np.interp(f_mhz_on, f_mhz_off, off_avg_raw).astype(np.float32)
    else:
        off_avg = off_avg_raw.astype(np.float32)

    # 1) Absolute Power (ON only)
    abs_png = f"{args.out}_absolute_power.png"
    plot_aaronia_like(
        f_mhz_on, pwr_on,
        abs_png,
        f"Wide Sweep {int(fmin)}–{int(fmax)} MHz (Absolute Power)",
        "Power (dB) (approx.)",
        args.abs_vmin, args.abs_vmax,
        normalize_waterfall=False,
        trace_ymin=args.abs_trace_ymin,
        trace_ymax=args.abs_trace_ymax,
    )

    # 2) Activity Highlight (Δ vs OFF) + normalized waterfall for visibility
    pwr_delta = pwr_on - off_avg[None, :]
    hl_png = f"{args.out}_activity_highlight.png"
    plot_aaronia_like(
        f_mhz_on, pwr_delta,
        hl_png,
        f"Wide Sweep {int(fmin)}–{int(fmax)} MHz (Activity Highlight: Δ vs OFF)",
        "Power (dB) (Δ vs OFF)",
        args.hl_vmin, args.hl_vmax,
        normalize_waterfall=True,
        trace_ymin=args.hl_trace_ymin,
        trace_ymax=args.hl_trace_ymax,
    )

    print(f"Saved:\n  {abs_png}\n  {hl_png}")

if __name__ == "__main__":
    main()
