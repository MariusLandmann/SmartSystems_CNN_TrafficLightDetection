# -*- coding: utf-8 -*-
"""Smart_Systems_Sample_Solution_Chapter_4_ImageWoof_dataset.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VKRMgz5FTEHTiNylYhTTp37Rb9P0w4J6
"""

# Commented out IPython magic to ensure Python compatibility.
"""Smart_Systems_Sample_Solution_Chapter_4_ImageWoof_dataset.ipynb"""

__author__ = "Marius Landmann"


"Main source: https://open.hpi.de/courses/neuralnets2020"
"Other sources which helped writing the code: https://github.com/MariusLandmann/SmartSystems_CNN_TrafficLightDetection/blob/master/Sources/Links.docx"

# TensorFlow ≥2.0 is required
# %tensorflow_version 2.x
!pip install --upgrade deeplearning2020
!pip install tensorflow_datasets
!pip install --upgrade tensorflow_datasets
!pip install tfds-nightly
import tensorflow as tf
from tensorflow import keras

assert tf.__version__ >= "2.0"

#Needs the provided GPU from Colab -> test if it is used
if not tf.config.list_physical_devices('GPU'):
    print("No GPU was detected. CNNs can be very slow without a GPU.")
    if IS_COLAB:
        print("Go to Runtime > Change runtime and select a GPU hardware accelerator.")


##Import required tools, layer types
import numpy as np
import tensorflow_datasets as tfds
#from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Dense, Activation, Input, \
  Dropout, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
from scipy.stats import reciprocal
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import gzip
from deeplearning2020 import helpers 

import tensorflow_datasets as tfds
!pip install h5py pyyaml
from __future__ import absolute_import, division, print_function
import os
# !pip install absl-py
# from absl import app
# from absl import flags

"""# Cloning and Pulling the GitHub repository"""

# Commented out IPython magic to ensure Python compatibility.
# Forked repository
repo_url = 'https://github.com/MariusLandmann/SmartSystems_CNN_TrafficLightDetection'


#Clone repository


# %cd /content

repo_dir_path = os.path.abspath(os.path.join('.', os.path.basename(repo_url)))

!git clone {repo_url}
# %cd {repo_dir_path}

print('Pull it so that we have the latest code/data')
!git pull

"""# Loading the Dataset
& preprocessing it
"""

from deeplearning2020.datasets import ImageWoof
train_data, test_data, classes= ImageWoof.load_data()

## Reshape and shuffle the dataset
def preprocess(image, label):
    resized_image = tf.image.resize(image, [300, 300])
    return resized_image, label

batch_size = 32
print('shape of training data before preprocessing: ', train_data)
train_data = train_data.shuffle(1000)


train_data = train_data.map(preprocess) \
  .batch(batch_size).prefetch(1)
test_data = test_data.map(preprocess) \
  .batch(batch_size).prefetch(1)
print('shape of training data after preprocessing: ', train_data)
print('shape of test data after preprocessing: ', test_data)

"""# Architecture, Training and Evaluation of the CNN"""

### model architecture
learning_rate=0.001
momentum=0.9
dense_neurons=300
a_filters=128
b_filters=256
first_kernel_size=(7,7)
n_kernel_size=(3,3)

activation='elu'


# input size of images must be 300x300 with RGB color
input_layer = Input(shape=(300, 300, 3))

## Layerstructure
# Convolutional Layers with Max Pooling
model = Conv2D(filters=a_filters, kernel_size=first_kernel_size, activation=activation)(input_layer)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = a_filters, kernel_size=n_kernel_size, activation=activation)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation)(model)
model = MaxPooling2D((2,2))(model)


model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation, padding='same')(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation, padding='same')(model)
model = MaxPooling2D((2,2))(model)



model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation, padding='same')(model)
# model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation, padding='same')(model)
# model = Conv2D(filters = b_filters, kernel_size=n_kernel_size, activation=activation, padding='same')(model)

# Fully-Connected-Classifier
model = Flatten()(model)
model = Dense(dense_neurons, activation=activation)(model)

model = Dense(dense_neurons / 2, activation='tanh')(model)

# Output Layer
output = Dense(10, activation="softmax")(model)

model = Model(input_layer, output)

# Compiling model
optimizer = keras.optimizers.SGD(lr=learning_rate, momentum=momentum)
model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer=optimizer,
    metrics=["accuracy"]
)
model.summary()

# Train the model
history = model.fit(
    train_data,
    epochs=13,
    validation_data = test_data
)

"""# Saving and Recreating the trained model"""

## Save the whole model
model.save('./trained_CNN/imagewoof/my_model_imagewoof.h5')

## Recreate whole model
new_model=keras.models.load_model('./trained_CNN/imagewoof/my_model_imagewoof.h5')
new_model.summary()

"""# DOWNLOAD created files
In this case downloading the previously created model.

Steps for downloading files manually: Anzeigen -> Inhalt -> Dateien (you can also display and download everything generated).
"""

# DOWNLOAD created files (in this case the previously created model) #################
from google.colab import files
files.download('./trained_CNN/imagewoof/my_model_imagewoof.h5')