import os
import cv2
import glob
import shutil

import tensorflow as tf
import keras 
from keras.models import Sequential
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten, Dropout
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.callbacks import TensorBoard

def lenet (input_shape, num_classes):
    ### from the beggining of CNN
    model = Sequential ()
    model.add (Conv2D (20, kernel_size = 5, padding = "same", input_shape = input_shape, activation = "relu"))
    model.add (MaxPooling2D (pool_size = (2, 2)))
    model.add (Conv2D (50, kernel_size = 5, padding = "same", activation = "relu"))
    model.add (MaxPooling2D (pool_size = (2, 2)))
    model.add (Flatten ())
    model.add (Dense (500, activation = "relu"))
    model.add (Dense (num_classes))
    model.add (Activation ("softmax"))
    return model


def load_correct_data (correct_data_dir_path, path_str = None):
    import xml.etree.ElementTree as ET

    if path_str == 'jj':
        xml_path_list = glob.glob ('../{}/*/*/*/*.xml'.format (correct_data_dir_path), recursive = True)
        print (xml_path_list)
        for xml_path in xml_path_list:
            tree = ET.parse (xml_path) 
            for item in tree.iter ():
                print (item.tag, item.attrib, item.text)
        exit ()



if __name__ == '__main__':

    model = lenet ((224, 224, 3), 5)
    model.summary ()

    ### bouding_box = [n_bb, x1, y1, x2, y2, label]
    load_correct_data ('annotation', path_str = 'jj')
