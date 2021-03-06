# -*- coding: utf-8 -*-
"""
Project: "Surprising Minds" at Sea Life Brighton, by Danbee Kim, Kerry Perkins, Clive Ramble, Hazel Garnade, Goncalo Lopes, Dario Quinones, Reanna Campbell-Russo, Robb Barrett, Martin Stopps, The EveryMind Team, and Adam Kampff. 
Analysis: Detect saccades 

Loads speed files generated by pm01_measure_speeds.py and finds the saccades
Categorizes saccades based on whether they occur during the calibration, octopus, or unique sequences of the experiment stimuli.
Outputs 3 .npz files for each subject (calibration, octopus, and unique) containing the speeds and timepoints of their saccades.

Resolution = 4ms per "timebucket", as that was the sampling rate used to generate the csv files of pupil tracking data. 

@author: Adam R Kampff and Danbee Kim
"""
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os.path

###################################
# SET CURRENT WORKING DIRECTORY
###################################
current_working_directory = os.getcwd()
###################################
# FUNCTIONS
###################################

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
    args = parser.parse_args()
    ###################################
    # SCRIPT LOGGER
    ###################################
    # grab today's date
    now = datetime.datetime.now()
    todays_datetime = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(filename="sd02DetectSaccades_" + todays_datetime + ".log", filemode='w', level=logging.INFO)
    ###################################
    # SOURCE DATA AND OUTPUT FILE LOCATIONS 
    ###################################
    data_folder, plots_folder = load_data()
    logging.info('DATA FOLDER: %s \n PLOTS FOLDER: %s' % (data_folder, plots_folder))
    print('DATA FOLDER: %s \n PLOTS FOLDER: %s' % (data_folder, plots_folder))
    ###################################
    # CREATE FOLDERS FOR SACCADE ("PEAKS") DATA [CAUTION, DELETES ALL PREVIOUS FILES]
    ###################################
    # make separate folder for each sequence
    calib_folder = data_folder + os.sep + 'calib_peaks'
    octo_folder = data_folder + os.sep + 'octo_peaks'
    sequences = [calib_folder, octo_folder]
    unique_folders = {}
    for stim in range(6):
        this_stim_folder = data_folder + os.sep + 'stim' + str(stim) + '_peaks'
        sequences.append(this_stim_folder)
        unique_folders[stim] = this_stim_folder
    for seq_folder in sequences:
        if not os.path.exists(seq_folder):
            logging.info("Creating speed data folder.")
            print("Creating speed data folder.")
            os.makedirs(seq_folder)
        if os.path.exists(seq_folder):
            # make sure it's empty
            logging.info("Deleting old speed data...")
            print("Deleting old speed data...")
            filelist = glob.glob(os.path.join(seq_folder, "*.npz"))
            for f in filelist:
                os.remove(f)
    ###################################
    # LOAD SPEED FILES
    ###################################
    speed_data_folder = data_folder + os.sep + 'speeds'
    trial_len_cutoff = 20000
    speed_files = glob.glob(speed_data_folder + os.sep + '*.data')
    num_files = len(speed_files)
    ###################################
    # SET TIME POINTS FOR EACH SEQUENCE
    ###################################
    calib_start = 0
    calib_end = 4431
    unique_start = 4431
    unique_ends = {0: 5962, 1: 6020, 2: 6660, 3: 6080, 4: 6670, 5: 7190}
    octo_len = 3980
    ###################################
    # INITIATE TRIAL COUNTERS FOR EACH SEQUENCE
    ###################################
    calib_trials = 0
    octo_trials = 0
    unique_trials = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    ###################################
    # DETECT SACCADES
    # CATEGORIZE INTO SEQUENCES (calibration, octopus, or unique)
    ###################################
    for s in range(6):
        count = 0
        for i, speed_file in enumerate(speed_files):
            # Get stimulus number
            trial_name = os.path.basename(speed_file)
            fields = trial_name.split(sep='_')
            eye = fields[1]
            stimulus = int(fields[0][-1])
            # Check if current stimulus number
            if(stimulus == s):
                # Load speed_file
                speed = np.fromfile(speed_file, dtype=np.float32)
                if len(speed) < trial_len_cutoff:
                    # Find "peaks" greater than some threshold?
                    low_threshold = 0.5
                    high_threshold = 1.5
                    peak_start_times = []
                    peak_stop_times = []
                    peaking = False
                    for i, sp in enumerate(speed):
                        # Look for a new peak
                        if(not peaking):
                            if(sp > high_threshold):
                                peaking = True
                                peak_start_times.append(i)
                        # Track ongoing peak    
                        else:
                            if(sp < low_threshold):
                                peaking = False       
                                peak_stop_times.append(i)
                    # Convert to arrays
                    peak_start_times = np.array(peak_start_times)
                    peak_stop_times = np.array(peak_stop_times)
                    # Throw out the first peak
                    peak_start_times = peak_start_times[1:]
                    peak_stop_times = peak_stop_times[1:]
                    # Throw out last peak if incomplete
                    if len(peak_start_times) > len(peak_stop_times):
                        peak_start_times = peak_start_times[:-1]
                    # Find peak durations
                    peak_durations = peak_stop_times - peak_start_times
                    # Find peak speed and indices
                    peak_speeds = []
                    peak_indices = []
                    for start, stop in zip(peak_start_times,peak_stop_times):
                        peak_speed = np.max(speed[start:stop])
                        peak_index = np.argmax(speed[start:stop])
                        peak_speeds.append(peak_speed)
                        peak_indices.append(start + peak_index)
                    # Convert to arrays
                    peak_speeds = np.array(peak_speeds)
                    peak_indices = np.array(peak_indices)
                    # Measure inter-peak_interval
                    peak_intervals = np.diff(peak_indices, prepend=[0])
                    # Filter for good saccades
                    good_peaks = (peak_intervals > 25) * (peak_durations < 30) * (peak_durations > 4) * (peak_speeds < 100)
                    peak_speeds = peak_speeds[good_peaks]
                    peak_indices = peak_indices[good_peaks]
                    peak_durations = peak_durations[good_peaks]
                    peak_intervals = peak_intervals[good_peaks]
                    # categorise peaks according to the sequence they happened within
                    # peak speeds
                    calib_peaks_speeds = []
                    octo_peaks_speeds = []
                    unique_peaks_speeds = []
                    # peak indices
                    calib_peaks_indices = []
                    octo_peaks_indices = []
                    unique_peaks_indices = []
                    for i, peak in enumerate(peak_indices):
                        if peak<=calib_end:
                            calib_peaks_indices.append(peak)
                            calib_peaks_speeds.append(peak_speeds[i])
                        if unique_start<peak<=unique_ends[stimulus]:
                            unique_peaks_indices.append(peak-unique_start)
                            unique_peaks_speeds.append(peak_speeds[i])
                        if unique_ends[stimulus]<peak<(unique_ends[stimulus]+octo_len):
                            octo_peaks_indices.append(peak-unique_ends[stimulus])
                            octo_peaks_speeds.append(peak_speeds[i])
                    calib_peaks_speeds = np.array(calib_peaks_speeds)
                    octo_peaks_speeds = np.array(octo_peaks_speeds)
                    unique_peaks_speeds = np.array(unique_peaks_speeds)
                    calib_peaks_indices = np.array(calib_peaks_indices)
                    octo_peaks_indices = np.array(octo_peaks_indices)
                    unique_peaks_indices = np.array(unique_peaks_indices)
                    # Store
                    # calibration
                    calib_path = calib_folder + os.sep + 'stim%d_%s_calib-peaks_%d.npz' % (stimulus, eye, calib_trials)
                    np.savez(calib_path, speeds=calib_peaks_speeds, indices=calib_peaks_indices)
                    calib_trials = calib_trials + 1
                    # octo
                    octo_path = octo_folder + os.sep + 'stim%d_%s_octo-peaks_%d.npz' % (stimulus, eye, octo_trials)
                    np.savez(octo_path, speeds=octo_peaks_speeds, indices=octo_peaks_indices)
                    octo_trials = octo_trials + 1
                    # unique
                    unique_path = unique_folders[stimulus] + os.sep + 'stim%d_%s_unique-peaks_%d.npz' % (stimulus, eye, unique_trials[stimulus])
                    np.savez(unique_path, speeds=unique_peaks_speeds, indices=unique_peaks_indices)
                    unique_trials[stimulus] = unique_trials[stimulus] + 1
                    # report progress
                    print('Calib trial count: {c}'.format(c=calib_trials))
                    print('Octo trial count: {o}'.format(o=octo_trials))
                    print('Unique stim {s} count: {u}'.format(s=stimulus, u=unique_trials[stimulus]))
                    print('---')
                    print('---')
        logging.info('Stimulus number {s} complete'.format(s=s+1))
        logging.info('Total unique stim {s} trial count: {u}'.format(s=s+1, u=unique_trials[stimulus]))
    logging.info('Total calibration trial count: {c}'.format(c=calib_trials))
    logging.info('Total octopus trial count: {o}'.format(o=octo_trials))


# FIN
