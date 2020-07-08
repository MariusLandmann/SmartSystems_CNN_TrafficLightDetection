# -*- coding: utf-8 -*-
"""Smart_Systems_CNN_Traffic_Light_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fAi6pxGqKmjzlf-Nbaodcyda8J3lyH9H
"""

# Commented out IPython magic to ensure Python compatibility.
"""Smart_Systems_CNN_Traffic_Light_Detection.ipynb: Chapter 7."""

__author__ = "Marius Landmann"
__credits__ = "Anna Dodik"


"Other sources which helped writing the code: https://github.com/MariusLandmann/SmartSystems_CNN_TrafficLightDetection/blob/master/Sources/Links.docx"

# TensorFlow ≥2.0 is required
# %tensorflow_version 2.x
# !pip install --upgrade deeplearning2020 
# !pip install tensorflow_datasets
# !pip install --upgrade tensorflow_datasets
# !pip install tfds-nightly

import tensorflow as tf
from tensorflow import keras

assert tf.__version__ >= "2.0"

#Benötigt die bereitgestellte GPU von Colab -> Test ob diese benutzt wird
if not tf.config.list_physical_devices('GPU'):
    print("No GPU was detected. CNNs can be very slow without a GPU.")
    if IS_COLAB:
        print("Go to Runtime > Change runtime and select a GPU hardware accelerator.")


##Importieren von benötigten Tools, Layertypen
import tensorflow as tf
from tensorflow import keras
import numpy as np
import tensorflow_datasets as tfds
from tensorflow.keras.layers import Dense, Activation, Input, \
  Dropout, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
from scipy.stats import reciprocal
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
!pip install absl-py
from absl import app
from absl import flags
import os

"""# Cloning and Pulling the GitHub repository"""

# Commented out IPython magic to ensure Python compatibility.
# https://towardsdatascience.com/deeppicar-part-6-963334b2abe0
# Forked repository
repo_url = 'https://github.com/MariusLandmann/SmartSystems_CNN_TrafficLightDetection'

#Clone repository
# %cd /content

repo_dir_path = os.path.abspath(os.path.join('.', os.path.basename(repo_url)))

!git clone {repo_url}
# %cd {repo_dir_path}

print('Pull it')
!git pull


##prepare training data --> from deeppicar
#installing packages for it
# %cd /content
!git clone --quiet https://github.com/tensorflow/models.git

!apt-get install -qq protobuf-compiler python-pil python-lxml python-tk

!pip install -q Cython contextlib2 pillow lxml matplotlib

!pip install -q pycocotools

# %cd /content/models/research
!protoc object_detection/protos/*.proto --python_out=.

os.environ['PYTHONPATH'] += ':/content/models/research/:/content/models/research/slim/'

"""# Loading the Dataset
& convert the xml files to a single csv file

& generate the TFRecord files

**Wichtig:** Die zwei Codes aus meinem GitHub benutzen! Eine lange Fehlersuche könnte ansonsten die Folge sein. generate_tfrecord.py findet man zwar online auf anderen Seiten allerdings sind diese auf Tensorflow 1.xx ausgelegt. Ich musste den Code teilweise umschreiben, damit er mit Tensorflow 2.xx verwendet werden kann
"""

# Commented out IPython magic to ensure Python compatibility.
#(https://towardsdatascience.com/deeppicar-part-6-963334b2abe0)
repo_dir_path = '/content/SmartSystems_CNN_TrafficLightDetection'
# %cd {repo_dir_path}/traffic_light_detection



# Convert train folder annotation xml files to a single csv file,
# generate the `label_map.pbtxt` file to `data/` directory as well.
!python code/xml_to_csv.py -i data/train -o data/annotations/train_labels.csv -l data/annotations

# Convert test folder annotation xml files to a single csv.
!python code/xml_to_csv.py -i data/test -o data/annotations/test_labels.csv



# Generate `train.record`
!python code/generate_tfrecord.py --csv_input=data/annotations/train_labels.csv --output_path=data/annotations/train.record --img_path=data/train --label_map data/annotations/label_map.pbtxt

# Generate `test.record`
!python code/generate_tfrecord.py --csv_input=data/annotations/test_labels.csv --output_path=data/annotations/test.record --img_path=data/test --label_map data/annotations/label_map.pbtxt


test_record_fname = repo_dir_path + '/traffic_light_detection/data/annotations/test.record'
train_record_fname = repo_dir_path + '/traffic_light_detection/data/annotations/train.record'
label_map_pbtxt_fname = repo_dir_path + '/traffic_light_detection/data/annotations/label_map.pbtxt'


print(type(test_record_fname))
print(len(test_record_fname))
print(test_record_fname)
#!cat data/annotations/train_labels.csv
#!cat {label_map_pbtxt_fname}
#!cat {train_record_fname}

#Recorddatei öffnen
file_testrecord=open(train_record_fname,'rb')
print(file_testrecord.readlines(2000))

"""# Ansatz X
Standart CNN Architektur gewählt, mit dem Ziel unser CNN mit unserem Datensatz im TFRecordformat zu trainieren.

Das Problem: kann bis jetzt nicht mit dem TFRecordformat trainiert werden, obwohl das Netz selber mit anderen Datensätzen (keine TFRecord files) funtionsfähig ist

Vermutung: Man braucht andere Funktionen wenn man den TFRecorddatensatz benutzen will
"""

###Architektur



# model
batch_size = 32
learning_rate=0.001
momentum=0.9
dense_neurons=300
n_filters=300
first_kernel_size=(7,7)

activation='elu'

# input size of images with RGB color
input_layer = Input(shape=(640, 480, 3))

# Convolutional Neural Network
# It consists of 5 stacked Convolutional Layers with Max Pooling
model = Conv2D(
    filters=256,
    kernel_size=(7,7),
    activation=activation
)(input_layer)
model = MaxPooling2D((2,2))(model)

model = Conv2D(
    filters = 256, 
    kernel_size=(3,3), 
    activation=activation
)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(
    filters = n_filters, 
    kernel_size=(3,3), 
    activation=activation
)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(
    filters = n_filters, 
    kernel_size=(3,3), 
    activation=activation
)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = n_filters, 
  kernel_size=(3,3), 
  activation=activation, 
  padding='same'
)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = n_filters, 
  kernel_size=(3,3), 
  activation=activation, 
  padding='same'
)(model)
model = MaxPooling2D((2,2))(model)

model = Conv2D(filters = n_filters, 
  kernel_size=(3,3), 
  activation=activation, 
  padding='same'
)(model)

# Fully-Connected-Classifier
model = Flatten()(model)
model = Dense(
    dense_neurons,
    activation=activation
)(model)

model = Dense(
    dense_neurons / 2,
    activation='tanh'
)(model)

# Output Layer
output = Dense(10, activation="softmax")(model)

CNN_model = Model(input_layer, output)

# Compiling model
optimizer = keras.optimizers.SGD(lr=learning_rate, momentum=momentum)
CNN_model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer=optimizer,
    metrics=["accuracy"]
)
CNN_model.summary()




#ALLES AUSKLAMMERN: markieren -> strg+shift+7

#!cat {test_record_fname}
#!cat {train_record_fname}

# Train the model
history2 = CNN_model.fit(
    train_record_fname,
    epochs=1,
    validation_data= test_record_fname
    
)




# model.fit(
#         x=train_record_fname,
#         #steps_per_epoch=1281167 // batch_size,
#         epochs=1
#         validation_data=test_record_fname,
#         #validation_steps=50000 // batch_size,
#         #callbacks=[learning_rate, model_ckpt, tensorboard],
#         # The following doesn't seem to help in terms of speed.
#         # use_multiprocessing=True, workers=4,
#         #epochs=epochs
#         )

"""#Eine komplexere Archetektur, welche normalerweise funktionieren würde:"""

# tf.keras.Sequential(
#     layers=None, name=None
# )





model = keras.Sequential()
model.add(Conv2D(64,(3,3),activation='relu',input_shape=(640,480,3), padding='same'))
model.add(Conv2D(64,(3,3),activation='relu',padding='same'))
model.add(Conv2D(64,(3,3),activation='relu',padding='same'))
model.add(MaxPooling2D((2,2),strides=(2,2)))

model.add(Conv2D(128,(3,3),activation='relu',padding='same'))
model.add(Conv2D(128,(3,3),activation='relu',padding='same'))
model.add(MaxPooling2D((2,2),strides=(2,2)))

model.add(Conv2D(256,(3,3),activation='relu',padding='same'))
model.add(Conv2D(256,(3,3),activation='relu',padding='same'))
model.add(Conv2D(256,(3,3),activation='relu',padding='same'))
model.add(MaxPooling2D((2,2),strides=(2,2)))

model.add(Conv2D(512,(3,3),activation='relu',padding='same'))
model.add(Conv2D(512,(3,3),activation='relu',padding='same'))
model.add(Conv2D(512,(3,3),activation='relu',padding='same'))
model.add(MaxPooling2D((2,2),strides=(2,2)))

model.add(Flatten())
model.add(Dense(600,activation='relu'))
model.add(Dense(600,activation='relu'))
model.add(Dense(2,activation='softmax'))

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',
metrics=['accuracy'])

model.fit(train_record_fname,test_record_fname,epochs=2)

"""# Neuer Ansatz A)
Eine andere Herangehensweise mit anderen Funktionen und Befehlen. Könnte sich rentieren das Netz in diese Richtung auszubauen bzw Betandteile zu übernehmen.

---wurde noch nicht auf das bestehende Netz angepasst---
"""

### A) Neuer Ansatz CNN_model https://androidkt.com/feeding-your-own-data-set-into-the-cnn-model-in-tensorflow/
labels=label_map_pbtxt_fname



_DEFAULT_IMAGE_SIZE = 252
_NUM_CHANNELS = 3
_NUM_CLASSES = 4
"""Model function for CNN."""
def cnn_model_fn(features, labels, mode):
    # Input Layer
    input_layer = tf.reshape(features["image"], [-1, _DEFAULT_IMAGE_SIZE, _DEFAULT_IMAGE_SIZE, 3])
    # Convolutional Layer #1
    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        filters=32,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu)
    # Pooling Layer #1
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
    # Convolutional Layer #2 and Pooling Layer #2
    conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=64,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu)
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
    # Dense Layer
    pool2_flat = tf.reshape(pool2, [-1, 126 * 126 * 64])
    dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)
    dropout = tf.layers.dropout(
        inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)
    # Logits Layer
    logits = tf.layers.dense(inputs=dropout, units=2)

### A) Neuer Ansatz  Generate Predictions
def cnn_model_fn(features, labels, mode):
    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

#Calculate Loss
#Calculate Loss (for both TRAIN and EVAL modes)
onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=2)
loss = tf.losses.softmax_cross_entropy(onehot_labels=onehot_labels, logits=logits)



#Training Operation
if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)




#Add evaluation metrics
eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}
return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

### A) Neuer Ansatz Benutzen der trainingsdaten bzw load them
def parse_record(raw_record, is_training):
    """Parse an ImageNet record from `value`."""
    keys_to_features = {
        'image/encoded':
            tf.FixedLenFeature((), tf.string, default_value=''),
        'image/format':
            tf.FixedLenFeature((), tf.string, default_value='jpeg'),
        'image/class/label':
            tf.FixedLenFeature([], dtype=tf.int64, default_value=-1),
        'image/class/text':
            tf.FixedLenFeature([], dtype=tf.string, default_value=''),
    }
    parsed = tf.parse_single_example(raw_record, keys_to_features)
    image = tf.image.decode_image(
        tf.reshape(parsed['image/encoded'], shape=[]),
        _NUM_CHANNELS)
    # Note that tf.image.convert_image_dtype scales the image data to [0, 1).
    image = tf.image.convert_image_dtype(image, dtype=tf.float32)
    image = vgg_preprocessing.preprocess_image(
        image=image,
        output_height=_DEFAULT_IMAGE_SIZE,
        output_width=_DEFAULT_IMAGE_SIZE,
        is_training=is_training)
    label = tf.cast(
        tf.reshape(parsed['image/class/label'], shape=[]),
        dtype=tf.int32)
    return {"image": image}, label

### A) Neuen Ansatz testen

###https://androidkt.com/feeding-your-own-data-set-into-the-cnn-model-in-tensorflow/


##Input functions
def input_fn(is_training, filenames, batch_size, num_epochs=1, num_parallel_calls=1):
    dataset = tf.data.TFRecordDataset(filenames)
    if is_training:
        dataset = dataset.shuffle(buffer_size=1500)
    dataset = dataset.map(lambda value: parse_record(value, is_training),
                          num_parallel_calls=num_parallel_calls)
    dataset = dataset.shuffle(buffer_size=10000)
    dataset = dataset.batch(batch_size)
    dataset = dataset.repeat(num_epochs)
    iterator = dataset.make_one_shot_iterator()
    features, labels = iterator.get_next()
    return features, labels
def train_input_fn(file_path):
    return input_fn(True, file_path, 100, None, 10)
def validation_input_fn(file_path):
    return input_fn(False, file_path, 50, 1, 1)

### A) Neuer Ansatz Training

#Create Estimator
classifier = tf.estimator.Estimator(model_fn=cnn_model_fn, model_dir="/tmp/convnet_model")

"""# Ansatz mit Transferlearning
Dieser Ansatz sollte sicher funktionieren, allerdings wird hierfür ein bereits trainiertes veröffentlichtes CNN benutz. Eine gute Anleitung findet man hier: https://towardsdatascience.com/deeppicar-part-6-963334b2abe0

Dies war allerdings nicht Bestandteil des Kurses, da wir den Aufbau und die Funktionsweise des neuronalen Netzes näherbringen wollten. Dies wäre beim Transferlearning nicht möglich gewesen, da die Hauptbestandteile eines fremden bestehenden Netzes einfach benutzt werden würde. Dieses wurde auch schon teilweise über mehrere Wochen durchgehend trainiert.

**-->** Die beste Möglichkeit wenn der lehrende Aspekt außer Acht gelassen werden würde

Wichtig: das CNN Modell muss allerdings "quantized" sein um Daten im TFRecordformat verarbeiten zu können
"""

# model configs are from Model Zoo github: 
# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md#coco-trained-models

### Empfohlenes Model für die TPU 
    #http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_quantized_300x300_coco_2019_01_03.tar.gz
   'ssd_mobilenet_v2_quantized': {
       'model_name': 'ssd_mobilenet_v2_quantized_300x300_coco_2019_01_03',
       'pipeline_file': 'ssd_mobilenet_v2_quantized_300x300_coco.config',
       'batch_size': 12
    },
    




# Pick the model you want to use
# Select a model in `MODELS_CONFIG`.
# Note: for Edge TPU, you have to:
# 1) start with a pretrained model from model zoo, such as above 4
# 2) Must be a quantized model, which reduces the model size significantly


# TPU# selected_model = 'ssd_mobilenet_v2_quantized'

# Name of the object detection model to use.
MODEL = MODELS_CONFIG[selected_model]['model_name']

# Name of the pipline file in tensorflow object detection API.
pipeline_file = MODELS_CONFIG[selected_model]['pipeline_file']

# Training batch size fits in Colabe's Tesla K80 GPU memory for selected model.
batch_size = MODELS_CONFIG[selected_model]['batch_size']




preprocess: shuffle and resize the images to a uniform size
def preprocess(image, label):
   resized_image = tf.image.resize(image, [640, 480])
   return resized_image, label


batch_size = 32
print('shape of training data before preprocessing: ', train_data)



train_data = train_data.map(preprocess) \
 .batch(batch_size).prefetch(1)
test_data = test_data.map(preprocess) \
 .batch(batch_size).prefetch(1)
print('shape of training data after preprocessing: ', train_data)
print('shape of test data after preprocessing: ', test_data)




train_data = train_data.shuffle(1000)

"""# Saving and Recreating the trained model"""

## Save the whole model
model.save('./trained_CNN/Smart_Truck/my_model_tld1.h5')

## Recreate whole model
new_model=keras.models.load_model('./trained_CNN/Smart_Truck/my_model_tld1.h5')
new_model.summary()

## Save the weights
model.save_weights('./trained_CNN/Smart_Truck/my_weights_tld1.h5')

## Restore the weights
model=create_model()
model.load_weights('./trained_CNN/Smart_Truck/my_weights_tld1.h5')

"""# DOWNLOAD created files
In this case downloading the previously created model.

Steps for downloading files manually: Anzeigen -> Inhalt -> Dateien (you can also display and download everything generated).
"""

from google.colab import files
files.download('./trained_CNN/Smart_Truck/my_model_tld1.h5')