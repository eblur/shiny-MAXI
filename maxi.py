##
## maxi.py -- Library of classes and convenience functions for playing
## with maxi data.
##
## 2022.02.09 - liac@umich.edu
##--------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

CAL_THRESH = 10.0

class MaxiData(object):
    def __init__(self, filename):
        data = np.loadtxt(filename)
        self.mjd   = data[:,0] # MJD of observation
        self.total = data[:,1] # 2-20 keV flux (phot/cm^2/s)
        self.soft  = data[:,3] # 2-4 keV
        self.med   = data[:,5] # 4-10 keV
        self.hard  = data[:,7] # 10-20 keV
        self.yunit = 'flux (phot/cm$^2$/s)'
        self.calibrated = False
        self.twoten = np.zeros_like(self.mjd)

    def plot(self, ax, band='total', **kwargs):
        assert band in ['total','soft','med','hard', '2-10']
        ax.set_xlabel('MJD')
        if band == 'total':
            ax.scatter(self.mjd, self.total, **kwargs)
            ax.set_ylabel('2-20 keV {}'.format(self.yunit))
        if band == 'soft':
            ax.scatter(self.mjd, self.soft, **kwargs)
            ax.set_ylabel('2-4 keV {}'.format(self.yunit))
        if band == 'med':
            ax.scatter(self.mjd, self.med, **kwargs)
            ax.set_ylabel('4-10 keV {}'.format(self.yunit))
        if band == 'hard':
            ax.scatter(self.mjd, self.hard, **kwargs)
            ax.set_ylabel('10-20 keV {}'.format(self.yunit))
        if band == '2-10':
            ax.scatter(self.mjd, self.twoten, **kwargs)
            ax.set_ylabel('10-20 keV {}'.format(self.yunit))
            print("Mean 2-10 keV flux: {:.4f}".format(np.mean(self.twoten)))
            print("Stdev 2-10 keV flux: {:.4f}".format(np.std(self.twoten)))
            
    def calibrate(self, cal_file, thresh=CAL_THRESH):
        cal_data = MaxiData(cal_file)

        # identify outliers in the calibration lc
        def id_outliers(yvals, thresh=thresh):
            return np.abs(yvals - np.median(yvals)) < (thresh * np.std(yvals))

        if not self.calibrated:
            ii = id_outliers(cal_data.total)
            cal_total = self.total / np.interp(self.mjd, cal_data.mjd[ii], cal_data.total[ii])

            ii = id_outliers(cal_data.soft)
            cal_soft = self.soft / np.interp(self.mjd, cal_data.mjd[ii], cal_data.soft[ii])

            ii = id_outliers(cal_data.med)
            cal_med = self.med / np.interp(self.mjd, cal_data.mjd[ii], cal_data.med[ii])

            ii = id_outliers(cal_data.hard)
            cal_hard = self.hard / np.interp(self.mjd, cal_data.mjd[ii], cal_data.hard[ii])

            data_twoten = self.soft + self.med
            cal_data_twoten = cal_data.soft + cal_data.med
            ii = id_outliers(cal_data_twoten)
            cal_twoten = data_twoten / np.interp(self.mjd, cal_data.mjd[ii], cal_data_twoten[ii])

            self.total = cal_total
            self.soft  = cal_soft
            self.med   = cal_med
            self.hard  = cal_hard
            self.twoten = cal_twoten
            self.calibrated = True
            self.yunit = 'flux (Crab)'
        else:
            print("This light curve has already been calibrated.")
