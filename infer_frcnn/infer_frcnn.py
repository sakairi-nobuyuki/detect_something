# coding: utf-8
import os
import glob
import pprint
import cv2
import numpy as np
import sys
import pickle
from optparse import OptionParser
import time
from keras_frcnn import config
from keras import backend as K
from keras.layers import Input
from keras.models import Model
from keras_frcnn import roi_helpers
from keras_frcnn.pascal_voc import pascal_voc_util
from keras_frcnn.pascal_voc_parser import get_data
from keras_frcnn import data_generators

from utils import get_bbox

import numpy as np
import sys
import pickle
from optparse import OptionParser
import time



# Method to transform the coordinates of the bounding box to its original size
def get_real_coordinates(ratio, x1, y1, x2, y2):
    real_x1 = int(round(x1 // ratio))
    real_y1 = int(round(y1 // ratio))
    real_x2 = int(round(x2 // ratio))
    real_y2 = int(round(y2 // ratio))

    return (real_x1, real_y1, real_x2 ,real_y2)
def format_img_size(img, C):
    """ formats the image size based on config """
    img_min_side = float(C.im_size)
    (height,width,_) = img.shape
        
    if width <= height:
        ratio = img_min_side/width
        new_height = int(ratio * height)
        new_width = int(img_min_side)
    else:
        ratio = img_min_side/height
        new_width = int(ratio * width)
        new_height = int(img_min_side)
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return img, ratio    

def format_img_channels(img, C):
    """ formats the image channels based on config """
    img = img[:, :, (2, 1, 0)]
    img = img.astype(np.float32)
    img[:, :, 0] -= C.img_channel_mean[0]
    img[:, :, 1] -= C.img_channel_mean[1]
    img[:, :, 2] -= C.img_channel_mean[2]
    img /= C.img_scaling_factor
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img

def format_img(img, C):
    """ formats an image for model prediction based on config """
    img, ratio = format_img_size(img, C)
    img_resized = img.copy ()
    img = format_img_channels(img, C)
    return img, img_resized, ratio

    

if __name__ == '__main__':

    config_output_filename = "config.pickle"

    with open(config_output_filename, 'rb') as f_in:
        C = pickle.load(f_in)
    from keras_frcnn import vgg as nn



    #img_path = "../annotation/test/MoroOkiHitomi13"        
    img_dir_path = "../annotation/test"
    #C.model_path = "models/vgg/frcnn_voc_0_2.331114761259407.hdf5"
    #C.model_path = "models/vgg/voc.hdf5"
    #C.model_path = "models/vgg/frcnn_voc_0_1.533816712998856.hdf5"
    #C.model_path = "models/vgg/frcnn_voc_0_2.262568243367597.hdf5"
    #C.model_path = "models/vgg/voc_old.hdf5"
    #C.model_path =  'models/rpn/rpn.vgg.weights.48-0.63.hdf5'
    #C.model_path = 'models/rpn/rpn.vgg.weights.48-2.04.hdf5'

    class_mapping = C.class_mapping

    if 'bg' not in class_mapping:
        class_mapping['bg'] = len(class_mapping)

    class_mapping = {v: k for k, v in class_mapping.items()}

    class_to_color = {class_mapping[v]: np.random.randint(0, 255, 3) for v in class_mapping}
    C.num_rois = int(10)

    num_features = 512
    print(class_mapping)

    
    if K.image_dim_ordering() == 'th':
        input_shape_img = (3, None, None)
        input_shape_features = (num_features, None, None)
    else:
        input_shape_img = (None, None, 3)
        input_shape_features = (None, None, num_features)


    img_input = Input(shape=input_shape_img)
    roi_input = Input(shape=(C.num_rois, 4))
    feature_map_input = Input(shape=input_shape_features)

    # define the base network (resnet here, can be VGG, Inception, etc)
    shared_layers = nn.nn_base(img_input, trainable=True)

    # define the RPN, built on the base layers
    num_anchors = len(C.anchor_box_scales) * len(C.anchor_box_ratios)
    rpn_layers = nn.rpn(shared_layers, num_anchors)

    classifier = nn.classifier(feature_map_input, roi_input, C.num_rois, nb_classes=len(class_mapping), trainable=True)

    model_rpn = Model(img_input, rpn_layers)
    #model_classifier_only = Model([feature_map_input, roi_input], classifier)
    model_classifier = Model([feature_map_input, roi_input], classifier)

    # model loading
    print('Loading weights from {}'.format(C.model_path))
    model_rpn.load_weights(C.model_path, by_name=True)
    model_classifier.load_weights(C.model_path, by_name=True)


    model_rpn.compile(optimizer='sgd', loss='mse')
    model_classifier.compile(optimizer='sgd', loss='mse')

    all_imgs = []

    classes = {}

    bbox_threshold = 0.05

    visualise = True

    ####  inference
    image_index_jpg = glob.glob ('./img/*.jpg')
    image_index_png = glob.glob ('./img/*.png')

    for img_path in image_index_jpg:
        img = cv2.imread (img_path)
        img_path = img_path.replace ("jpg", "png")
        cv2.imwrite (img_path, img)
    image_index = []
    image_index.extend (image_index_jpg)
    image_index.extend (image_index_png)

    print ("list of images to infer: ")
    pprint.pprint (image_index)
    #image_index = sorted(img_pathes)
    
    for idx, img_name in enumerate(image_index):
        if not img_name.lower().endswith(('.bmp', '.jpeg', '.jpg', '.png', '.tif', '.tiff')):
            continue
        print("inference image path:", img_name)
        st = time.time()
        filepath = img_name
        
        #print ("file size of {} is {}".format (filepath, os.path.getsize (filepath)))
        if (os.path.getsize (filepath)) < 1000:
            print ("empty img: ", filepath)
            continue

        img = cv2.imread(filepath)
        
        X, img_rect, ratio = format_img(img, C)
        
        img_scaled = (np.transpose(X[0,:,:,:],(1,2,0)) + 127.5).astype('uint8')

        if K.image_dim_ordering() == 'tf':
            X = np.transpose(X, (0, 2, 3, 1))

        # get the feature maps and output from the RPN
        [Y1, Y2, F] = model_rpn.predict(X)
    
        # infer roi
        R = roi_helpers.rpn_to_roi(Y1, Y2, C, K.image_dim_ordering(), overlap_thresh=0.8)
        # get bbox
        #all_dets, bboxes, probs = get_bbox(R, C, model_classifier, class_mapping, F, ratio, bbox_threshold=0.5)
        # convert from (x1,y1,x2,y2) to (x,y,w,h)
        R[:, 2] -= R[:, 0]
        R[:, 3] -= R[:, 1]

        # apply the spatial pyramid pooling to the proposed regions
        bboxes = {}
        probs = {}

        for jk in range(R.shape[0]//C.num_rois + 1):
            ROIs = np.expand_dims(R[C.num_rois*jk:C.num_rois*(jk+1), :], axis=0)
            if ROIs.shape[1] == 0:
                break
            if jk == R.shape[0]//C.num_rois:
                #pad R
                curr_shape = ROIs.shape
                target_shape = (curr_shape[0],C.num_rois,curr_shape[2])
                ROIs_padded = np.zeros(target_shape).astype(ROIs.dtype)
                ROIs_padded[:, :curr_shape[1], :] = ROIs
                ROIs_padded[0, curr_shape[1]:, :] = ROIs[0, 0, :]
                ROIs = ROIs_padded

            [P_cls, P_regr] = model_classifier.predict([F, ROIs])

            for ii in range(P_cls.shape[1]):
                if np.max(P_cls[0, ii, :]) < bbox_threshold: #or np.argmax(P_cls[0, ii, :]) == (P_cls.shape[2] - 1):
                    print("no boxes detected")
                    continue
                cls_name = class_mapping[np.argmax(P_cls[0, ii, :])]

                if cls_name not in bboxes:
                    bboxes[cls_name] = []
                    probs[cls_name] = []
                (x, y, w, h) = ROIs[0, ii, :]

                cls_num = np.argmax(P_cls[0, ii, :])
                try:
                    (tx, ty, tw, th) = P_regr[0, ii, 4*cls_num:4*(cls_num+1)]
                    tx /= C.classifier_regr_std[0]
                    ty /= C.classifier_regr_std[1]
                    tw /= C.classifier_regr_std[2]
                    th /= C.classifier_regr_std[3]
                    x, y, w, h = roi_helpers.apply_regr(x, y, w, h, tx, ty, tw, th)
                except:
                    pass
                bboxes[cls_name].append([C.rpn_stride*x, C.rpn_stride*y, C.rpn_stride*(x+w), C.rpn_stride*(y+h)])
                probs[cls_name].append(np.max(P_cls[0, ii, :]))
        print ("in {}: ".format (filepath))
        
        
        #img_rect = img
        print ("  size of infer res: {}".format (len (bboxes)))
        print ("  of which contents: ", bboxes, probs)
        for (bbox_key, bbox_values), (prob_key, prob_values) in zip (bboxes.items (), probs.items ()):
            if bbox_key == 'bg':  continue
            print ("bbox class: {}, prob class: {}".format (bbox_key, prob_key))
            for bbox_value, prob_value in zip (bbox_values, prob_values):
                if prob_value < 0.5: continue
                colour = (255, 0, 0)
                print ('  prob: ', prob_value)

            if bbox_key == 'fc' or bbox_key == 'gl':
                for bbox_value, prob_value in zip (bbox_values, prob_values):
                    if prob_value < 0.5: continue
                    if bbox_key == 'fc': colour = (255, 0, 0)
                    if bbox_key == 'gl':    colour = (0, 255, 0)
                    print ('  prob: ', prob_value)
                    cv2.rectangle (img_rect, (bbox_value[0], bbox_value[1]), (bbox_value[2], bbox_value[3]), colour)
                    cv2.putText(img_rect, '%0.3f' % prob_value, (bbox_value[0], bbox_value[1]), cv2.FONT_HERSHEY_PLAIN, 1, colour, 1, cv2.LINE_AA)
        rect_file_name = 'rect_' + str (os.path.basename (filepath))
        rect_file_path =  os.path.join (os.path.dirname (filepath), rect_file_name)
        print ("rect file to save: {}".format (rect_file_path))
        cv2.imwrite (rect_file_path, img_rect)
            #    print ("  bbox: {}, prob: {}".format (bbox_value, prob_value))
            
