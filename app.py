
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import requests

from shiny import App, render, ui, reactive

from maxi import MaxiData


# key-value pairs for known labels vs MAXI labels
MAXI_LABELS = {'gx339':'J1702-487'}

def scrape_maxi_lightcurve(label, outfile):
    maxi_http = requests.get(f"http://maxi.riken.jp/star_data/{label}/{label}_g_lc_1day_all.dat")
    f = open(outfile, 'w')
    f.write(maxi_http.text)
    f.close()
    return MaxiData(outfile)

# Crab data (calibration light curve)
CRAB_LABEL = 'J0534+220'
crab_data = scrape_maxi_lightcurve(CRAB_LABEL, 'crab.dat')

app_ui = ui.page_fluid(
    ui.h2("Fun with MAXI light curves"),
    ui.markdown(""" 
        This app makes plots of [MAXI](http://maxi.riken.jp/top/index.html) 
        light curve data!
        """),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_select("target", "Target Name",
                                   dict(gx339="GX 339-4")),
            #ui.input_radio_buttons("band", "Energy Band",
            #                       dict(total="2-20 keV", soft="2-4 keV", med="4-10 keV", hard="10-20 keV"))
            ui.input_slider("mjd_range", "MJD", crab_data.mjd[0], crab_data.mjd[-1],
                            [crab_data.mjd[-1]-100, crab_data.mjd[-1]])
            ),
        ui.panel_main(
            #ui.output_text_verbatim("txt"),
            ui.output_plot("plot")
            )
        )
    )

def server(input, output, session):
    # https://shiny.posit.co/py/docs/reactive-calculations.html
    @reactive.Calc
    def target():
        # Load and calibrate the data
        label = MAXI_LABELS[input.target()]
        data  = scrape_maxi_lightcurve(label, 'target.dat')
        #data = MaxiData('J1702-487_g_lc_1day_all.dat')
        data.calibrate(cal_file='crab.dat', thresh=5.0)
        return data
    
    @output
    @render.plot
    def plot():
        data = target()
        # Make the plot
        fig = plt.figure(figsize=(8,6))
        gs = GridSpec(2, 1, height_ratios=(1,2))
        ax0 = plt.subplot(gs[0])
        # Plot the calibrated light curve
        #data.plot(ax0, input.band(), s=10, color='0.5', alpha=0.5)
        data.plot(ax0, 'total', s=10, color='0.5', alpha=0.5)
        ax0.set_title('2-20 keV (Crab)', size=10)
        ax0.set_ylabel('')
        # With the highlighted region
        mjdr = input.mjd_range()
        ax0.axvspan(mjdr[0], mjdr[1], color='r', alpha=0.3)
        # Plot the hardness ratio
        hratio = data.med / data.soft
        ax1 = plt.subplot(gs[1])
        ax1.scatter(hratio, data.total, s=10, color='0.5', alpha=0.5)
        # Plot the values from the highlighted region
        imjd = (data.mjd >= mjdr[0]) & (data.mjd <= mjdr[1])
        ax1.scatter(hratio[imjd], data.total[imjd], s=10, color='r')
        # Axes labels
        ax1.set_ylabel('2-20 keV flux [ph/cm$^2$/s]', size=12)
        ax1.set_xlabel("Hardness ratio (4-10 keV / 2-4 keV)", size=14)
        return fig

app = App(app_ui, server)
