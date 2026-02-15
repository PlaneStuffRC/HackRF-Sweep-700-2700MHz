1) Capture (wide sweep 750–2700 MHz)

OFF (baseline):

hackrf_sweep -f 750:2700 -w 2000000 -l 20 -g 6 > wide_off_750_2700_B.csv


ON (ELRS running):

hackrf_sweep -f 750:2700 -w 2000000 -l 20 -g 6 > wide_on_750_2700_B.csv

2) Generate the two plots (one command)

This generates both:

..._absolute_power.png

..._activity_highlight.png

python elrs_wide_plot_onecmd.py --on wide_on_750_2700_B.csv --off wide_off_750_2700_B.csv --range 750:2700 --out wide_750_2700_B

