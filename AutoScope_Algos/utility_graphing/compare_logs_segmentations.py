"""
    File name: compare_logs_segmentation.py
    Author: Sidney Primas
    Python Version: 2.7
    Description: Compare multiple logs. 
"""

import matplotlib.pyplot as plt
from scipy import signal
import pandas as PD
import numpy as np
import re
import sys
import bisect

# Import homebrew functions
sys.path.append("./urine_particles/data/clinical_experiment/log/20180130_semantic_seg/final_selection_results_updated_more_images/")
import config 

### Execution Notes ####
# Be careful, list of log metrics are strings. Need to convert them to ints.. 
# ToDo: Poorly written and structured code. Need to rewrite/restructure. 


""" Configuration Variables """
averaging_window = 1
plot_type = "val" # select "val" for the validation accuracy and "train" for the training accuracy



def main():


	log_data = process_log()


	if (plot_type == "train"):
		output_accuracy_plots(log_data["all_total_images"], log_data["all_train_accuracy"], log_data["min_image_count"])
	if (plot_type == "val"):
		output_accuracy_plots(log_data["all_total_images"], log_data["all_val_accuracy"], log_data["min_image_count"])


def process_log():
	"""
	Description: Loads all the log files from config, extracts the relevant parameters, and returns preprocessed lists of the results. 
	Returns
	log_data: A dictionary of lists with metrics from the log. 
	"""
	# Use to track the log with the least images. 
	min_image_count = 0 # needs to be a local, since we update the variable. 
	

	# Variables that aggregate data across all logs. 
	all_total_images = []
	all_train_accuracy = []
	all_val_accuracy = []
	all_batch_loss = []

	### Extract relevant data from the logs ###
	for file_name in config.logs['file_name']: 

		filename = config.log_directory + file_name

		# Variables that aggregate data from single log. 
		total_images = []
		train_accuracy = []
		val_accuracy = []
		batch_loss = []

		# Parse through log to pull out summary results. 
		with open(filename) as f:
			for line in f:
				# Process summary line
				if (line.find("Step: ") >= 0):
					# Handle training accuracy
					total_images.extend(re.findall("Images Trained: (\d+)", line))
					train_accuracy.extend(re.findall("Training accuracy: (\d\.\d+)", line))
					batch_loss.extend(re.findall("Batch loss: (\d+\.\d+)", line))


				
				val_acc = re.findall("Validation accuracy: (\d\.\d+)", line)
				if (len(val_acc) >= 0):
					val_accuracy.extend(val_acc)


		# Convert from Strings to Numbers (float or int). Then, append to global struct.
		total_images = map(int, total_images)
		train_accuracy = map(float, train_accuracy)
		val_accuracy= map(float, val_accuracy)
		batch_loss = map(float, batch_loss)


		# Track the number of iterations (in terms of images) that all datasets have gotten to. 
		# Allows for comparison across datasets based on the number of images used for training. 
		if ((min_image_count == 0) or (min_image_count > (total_images[-1]))):
			min_image_count = total_images[-1]


		# Apply moving window average, and then append the metrics from the logs to their respective lists. 
		all_total_images.append(total_images)
		train_accuracy = PD.Series(train_accuracy)
		train_accuracy = train_accuracy.rolling(window=averaging_window,center=False).mean() # Rolling Average (use built in pandas function)
		all_train_accuracy.append(train_accuracy)
		val_accuracy = PD.Series(val_accuracy)
		val_accuracy = val_accuracy.rolling(window=averaging_window,center=False).mean() # Rolling Average (use built in pandas function)
		all_val_accuracy.append(val_accuracy)
		all_batch_loss.append(batch_loss)


	log_data = {
		"min_image_count": min_image_count, 
		"all_total_images": all_total_images, 
		"all_train_accuracy": all_train_accuracy, 
		"all_val_accuracy": all_val_accuracy
	}

	return log_data

def get_index_of_imageNum(image_count_list, count):
	index_before_count = bisect.bisect_left(image_count_list, int(count), lo=0, hi=len(image_count_list))
	return index_before_count



def output_accuracy_plots(all_total_images, all_accuracy, min_image_count):
	"""
	Description: Plot the accuracy obtained from the log.
	"""
	print min_image_count
	for n in range(len(all_total_images)):

		min_image_index = get_index_of_imageNum(all_total_images[n], min_image_count)
		# Print accuracy stats. 
		print " Res of %s: Number of Images (%d), Accuracy (%f)"%(config.logs['file_name'][n], all_total_images[n][min_image_index],all_accuracy[n][min_image_index])
		print "Total Images (%d), Final Accuracy (%f)"%(all_total_images[n][-1], all_accuracy[n].iloc[-1])

		# Visualize the accuracy (across all data)
		fig = plt.figure(1)
		plt.plot(all_total_images[n], all_accuracy[n]*100, label = config.logs['legend'][n], linewidth=4.0)
		fig.patch.set_facecolor('white')
		plt.xlabel("Number of Training Cycles", fontsize="20")
		plt.ylabel("Segmentation Accuracy (%)", fontsize="20")
		plt.legend(loc='lower right', prop={'size':12}, frameon=False)
		# axes = fig.axes[0]
		# axes.set_ylim([0,100])

		# Visualize the accuracy (across all data)
		fig = plt.figure(2)
		plt.plot(all_total_images[n][:min_image_index], all_accuracy[n][:min_image_index]*100, label = config.logs['legend'][n], linewidth=4.0)
		fig.patch.set_facecolor('white')
		plt.xlabel("Number of Training Cycles", fontsize="20")
		plt.ylabel("Segmentation Accuracy (%)", fontsize="20")
		plt.legend(loc='lower right', prop={'size':12}, frameon=False)
		#axes = fig.axes[0]
		#axes.set_ylim([98,100])
		#axes.set_xlim([1500,21000])


	plt.show()


if __name__ == "__main__":
	main()