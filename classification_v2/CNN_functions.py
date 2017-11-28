# Import basic libraries
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import logging
import json

from tensorflow.python.keras._impl.keras import backend as K


def save_history_to_file(history, file_path):

	with open(file_path, 'w') as outfile:
	    json.dump(history, outfile)

def print_configurations(config):
	all_class_attributes =  dir(config) #Get all class attributes. 
	local_class_attriubutes = [a for a in all_class_attributes if not a.startswith('__') and not callable(getattr(config,a))]

	config.logger.info("###### CONFIGURATION ######")
	# Print all configuration attributes
	for attribute in local_class_attriubutes: 
		# Since attribute is a string, need to use exec to execute function. 
		exec('config.logger.info("%s: %s"%(attribute, config.' + attribute +'))')
	config.logger.info("###### CONFIGURATION ###### \n\n")
		 



def create_logger(log_dir, file_name, log_name): 
		logger = logging.getLogger(log_name)
		logger.setLevel(logging.INFO) 
		if (file_name == None):
			file_name = datetime.strftime(datetime.now(), 'log_%Y%m%d_%H-%M-%S.log')

		fileHandler = logging.FileHandler(log_dir + file_name, 'w')
		fileHandler.setLevel(logging.INFO) 
		logger.addHandler(fileHandler)
		consoleHandler = logging.StreamHandler()
		logger.addHandler(consoleHandler)
		#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		#fileHandler.setFormatter(formatter)
		#consoleHandler.setFormatter(logFormatter)
		return logger

def freeze_lower_layers(model, layer_name):
	"""
	Freeze layers below layer_name for Transfer Learning. Need to compile to take into effect. 
	Freeze layer_name and all layers below it. 
	Args:
	model: keras model
	layer_name: Freeze layer_name and all layers below it. 
	"""
	train_this_layer = False
	for layer in model.layers: 
		layer.trainable = train_this_layer

		# Train layers above layer_name
		if layer.name == layer_name: 
			train_this_layer = True


def plot_training(history):
	acc = history.history['acc']
	val_acc = history.history['val_acc']
	loss = history.history['loss']
	val_loss = history.history['val_loss']
	epochs = range(len(acc))

	plt.plot(epochs, acc, 'r.')
	plt.plot(epochs, val_acc, 'r')
	plt.legend(["Train Accuracy", "Validation Accuracy"])
	plt.title('Training and validation accuracy')

	plt.figure()
	plt.plot(epochs, loss, 'r.')
	plt.plot(epochs, val_loss, 'r-')
	plt.legend(["Train Loss", "Validation Validation"])
	plt.title('Training and validation loss')
	plt.show()

