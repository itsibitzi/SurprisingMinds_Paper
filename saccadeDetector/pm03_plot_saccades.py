# -*- coding: utf-8 -*-
"""
Project: "Surprising Minds" at Sea Life Brighton, by Danbee Kim, Kerry Perkins, Clive Ramble, Hazel Garnade, Goncalo Lopes, Dario Quinones, Reanna Campbell-Russo, Robb Barrett, Martin Stopps, The EveryMind Team, and Adam Kampff. 
Analysis: Plot saccade rasters for each sequence (calibration, octopus, unique) 

Loads saccade files generated by pm02_detect_saccades.py and plots saccades as raster plots.
Categorizes saccades based on size of saccade (big, medium, small).
Outputs a .png file for each sequence in the experimental stimuli (calibration, octopus, unique); the plot is a raster file of the saccades made by all experiment participants.

Resolution = 4ms per "timebucket", as that was the sampling rate used to generate the csv files of pupil tracking data. 

Optional flags:
"--big_upper": Upper bound for saccade speeds categorized as "big" saccades (current default = 75)
"--big_lower": Lower bound for saccade speeds categorized as "big" saccades (current default = 45)
"--med_upper": Upper bound for saccade speeds categorized as "medium" saccades (current default = 25)
"--med_lower": Lower bound for saccade speeds categorized as "medium" saccades (current default = 15)
"--lil_upper": Upper bound for saccade speeds categorized as "little" saccades (current default = 15)
"--lil_lower": Lower bound for saccade speeds categorized as "little" saccades (current default = 1)

@author: Adam R Kampff and Danbee Kim
"""
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os.path
import argparse
import logging
import time
from joblib import Parallel, delayed

###################################
# SET CURRENT WORKING DIRECTORY
###################################
current_working_directory = os.getcwd()
###################################
# FUNCTIONS
###################################
def plot_sequence(seq_type):
    peak_files = seq_peak_files[seq_type]
    seq_trial_count = len(peak_files)
    # set figure save path and title
    figure_name = 'DetectedSaccades_' + seq_type + '_' + todays_datetime + '.png'
    figure_path = os.path.join(plots_folder, figure_name)
    figure_title = 'Detected Saccades during sequence {s}, categorized by speed, N={n}'.format(s=seq_type, n=seq_trial_count)
    plt.figure(figsize=(14, 14), dpi=fsize)
    plt.suptitle(figure_title, fontsize=12, y=0.98)
    if seq_type == 'calib':
        alpha_plotting = 0.07
        x_max = 4431
    elif seq_type == 'octo':
        alpha_plotting = 0.07
        x_max = 3980
    else:
        alpha_plotting = 0.3
        x_max = 2759
    count = 0
    start_time = time.time_ns()
    for i, peak_file in enumerate(peak_files):
        # Get stimulus number
        trial_name = os.path.basename(peak_file)
        fields = trial_name.split(sep='_')
        eye = fields[1]
        stimulus = int(fields[0][-1])
        seq = fields[2].split('-')[0]
        # Load peak_file
        peaks = np.load(peak_file)
        peak_speeds = peaks['speeds']
        peak_indices = peaks['indices']
        # Make some peak categories
        big_speeds = (peak_speeds < big_upper) * (peak_speeds > big_lower)
        med_speeds = (peak_speeds < med_upper) * (peak_speeds > med_lower)
        lil_speeds = (peak_speeds < lil_upper) * (peak_speeds > lil_lower)
        # Plot a saccade raster
        ## big saccades
        num_peaks = np.sum(big_speeds)
        row_value = count*np.ones(num_peaks)
        plt.subplot(3,1,1)
        plt.ylabel('Individual Trials', fontsize=9)
        plt.title('Big Saccades (pupil movements between {l} and {u} pixels per frame)'.format(l=big_lower, u=big_upper), fontsize=10, color='grey', style='italic')
        plot_xticks = np.arange(0, x_max, step=250)
        plt.xticks(plot_xticks, ['%.1f'%(x/250) for x in plot_xticks])
        plt.plot(peak_indices[big_speeds], row_value, 'r.', alpha=alpha_plotting)
        ## medium saccades
        num_peaks = np.sum(med_speeds)
        row_value = count*np.ones(num_peaks)
        plt.subplot(3,1,2)
        plt.ylabel('Individual Trials', fontsize=9)
        plt.title('Medium Saccades (pupil movements between {l} and {u} pixels per frame)'.format(l=med_lower, u=med_upper), fontsize=10, color='grey', style='italic')
        plot_xticks = np.arange(0, x_max, step=250)
        plt.xticks(plot_xticks, ['%.1f'%(x/250) for x in plot_xticks])
        plt.plot(peak_indices[med_speeds], row_value, 'b.', alpha=alpha_plotting)
        ## little saccades
        num_peaks = np.sum(lil_speeds)
        row_value = count*np.ones(num_peaks)
        plt.subplot(3,1,3)
        plt.ylabel('Individual Trials', fontsize=9)
        plt.xlabel('Time (seconds) since beginning of this sequence', fontsize=9)
        plt.title('Small Saccades (pupil movements between {l} and {u} pixels per frame)'.format(l=lil_lower, u=lil_upper), fontsize=10, color='grey', style='italic')
        plot_xticks = np.arange(0, x_max, step=250)
        plt.xticks(plot_xticks, ['%.1f'%(x/250) for x in plot_xticks])
        plt.plot(peak_indices[lil_speeds], row_value, 'k.', alpha=alpha_plotting)
        # Report
        end_time = time.time_ns()
        elapsed_time = (end_time - start_time)/1000000000
        logging.info('Sequence type: {s}, Trial count: {c}'.format(s=seq_type, c=count))
        logging.info('Elapsed time: {e}'.format(e=elapsed_time))
        logging.info('Rate: {r}'.format(r=count/elapsed_time))
        print('Sequence type: {s}, Trial count: {c}'.format(s=seq_type, c=count))
        # print('Elapsed time: {e}'.format(e=elapsed_time))
        # print('Rate: {r}'.format(r=count/elapsed_time))
        print("--")
        print("--")
        count = count + 1
    # save and display
    #plt.subplots_adjust(hspace=0.5)
    plt.savefig(figure_path)
    plt.show(block=False)
    plt.pause(1)
    plt.close()

##########################################################
#### MODIFY THIS FIRST FUNCTION BASED ON THE LOCATIONS OF:
# 1) data_dir (folder with all intermediate data for this project, used as both input and output location of data for this script)
# 2) plots_dir (parent folder for all plots output by this script)
##########################################################
def load_data():
    data_dir = r'C:\Users\taunsquared\Dropbox\SurprisingMinds\analysis\intermediates'
    plots_dir = r'C:\Users\taunsquared\Dropbox\SurprisingMinds\analysis\plots\saccade_detector'
    return data_dir, plots_dir
##########################################################

##########################################################
# BEGIN SCRIPT
##########################################################
if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='''Detect saccades.
        Loads speed files generated by pm01_measure_speeds.py and finds the saccades
        Categorizes saccades based on whether they occur during the calibration, octopus, or unique sequences of the experiment stimuli.
        Outputs 3 .npz files for each subject (calibration, octopus, and unique) containing the speeds and timepoints of their saccades.
        WARNING: This script overwrites saccade ("peaks") data outputted from previous runs of this script. TO SAVE OLD SACCADE DATA, RENAME THE FOLDER CONTAINING OLD SACCADE DATA.
        Resolution = 4ms per "timebucket", as that was the sampling rate used to generate the csv files of pupil tracking data. ''')
    parser.add_argument("--a", nargs='?', default="check_string_for_empty")
    parser.add_argument("--big_upper", nargs=1, type=int, default=75, help="Upper bound for saccade speeds categorized as 'big' saccades (current default = 75)")
    parser.add_argument("--big_lower", nargs=1, type=int, default=45, help="Lower bound for saccade speeds categorized as 'big' saccades (current default = 45)")
    parser.add_argument("--med_upper", nargs=1, type=int, default=25, help="Upper bound for saccade speeds categorized as 'medium' saccades (current default = 25)")
    parser.add_argument("--med_lower", nargs=1, type=int, default=15, help="Lower bound for saccade speeds categorized as 'medium' saccades (current default = 15)")
    parser.add_argument("--lil_upper", nargs=1, type=int, default=15, help="Upper bound for saccade speeds categorized as 'little' saccades (current default = 15)")
    parser.add_argument("--lil_lower", nargs=1, type=int, default=1, help="Lower bound for saccade speeds categorized as 'little' saccades (current default = 1)")
    args = parser.parse_args()
    ###################################
    # SCRIPT LOGGER
    ###################################
    # grab today's date
    now = datetime.datetime.now()
    todays_datetime = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(filename="pm03PlotSaccades_" + todays_datetime + ".log", filemode='w', level=logging.INFO)
    ###################################
    # SOURCE DATA AND OUTPUT FILE LOCATIONS 
    ###################################
    data_folder, plots_folder = load_data()
    logging.info('DATA FOLDER: %s \n PLOTS FOLDER: %s' % (data_folder, plots_folder))
    print('DATA FOLDER: %s \n PLOTS FOLDER: %s' % (data_folder, plots_folder))
    ###################################
    # SET BOUNDARIES FOR SIZE CATEGORIES OF SACCADE
    ###################################
    big_upper = args.big_upper
    big_lower = args.big_lower
    med_upper = args.med_upper
    med_lower = args.med_lower
    lil_upper = args.lil_upper
    lil_lower = args.lil_lower
    ###################################
    # COLLECT SACCADE FILES FOR EACH SEQUENCE
    ###################################
    seq_peak_files = {}
    seq_peak_files['calib'] = glob.glob(data_folder + os.sep + '*calib_peaks' + os.sep + '*.npz')
    seq_peak_files['octo'] = glob.glob(data_folder + os.sep + '*octo_peaks' + os.sep + '*.npz')
    for stim in range(6):
        this_unique_peak_files = glob.glob(data_folder + os.sep + 'stim' + str(stim) + '_peaks' + os.sep + '*.npz')
        seq_peak_files[str(stim)] = this_unique_peak_files
    ###################################
    # PLOT RASTERS OF SACCADES DURING EACH SEQUENCE
    ###################################
    fsize = 200 #dpi
    # parallelize the plotting process to make it faster
    Parallel()(delayed(plot_sequence)(seq_type) for seq_type in seq_peak_files.keys())
# FIN