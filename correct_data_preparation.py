import os
import glob
import shutil
import xmltodict
import json
import pprint
import xml.etree.ElementTree as ET

def file_read(path):
    with open(path, 'r') as file:
        text = file.read()
    return text

def extract_bboxes_inf (ord_dict):
    sub_dict = {}
    sub_dict['attr'] = ord_dict['name']
    sub_dict['x1'] = ord_dict['bndbox']['xmin']
    sub_dict['y1'] = ord_dict['bndbox']['ymin']
    sub_dict['x2'] = ord_dict['bndbox']['xmax']
    sub_dict['y2'] = ord_dict['bndbox']['ymin']

    return sub_dict

def load_correct_data (correct_data_dir_path, path_str = None):
    #import xml.etree.ElementTree as ET
    correct_list = []
    if path_str == 'jj':
        xml_path_list = glob.glob ('../../{}/*/*/*/*.xml'.format (correct_data_dir_path), recursive = True)
        #print (xml_path_list)
        for xml_path in xml_path_list:
            dict = xmltodict.parse (file_read (xml_path))
            correct_sub_dict = {}
            correct_sub_dict['path'] = dict['annotation']['path']
            annotation_list = []
            if 'object' in dict['annotation'].keys ():
                if type (dict['annotation']['object']) != list:
                    annotation_list.append (extract_bboxes_inf (dict['annotation']['object']))
                else:
                    for sub_dict in dict['annotation']['object']:  
                        annotation_list.append (extract_bboxes_inf (sub_dict))
            correct_sub_dict['annotation'] = annotation_list
            correct_list.append (correct_sub_dict)
        #pprint.pprint (correct_list)
    return (correct_list)


if __name__ == '__main__':
    ### bouding_box = [n_bb, x1, y1, x2, y2, label]
    load_correct_data ('annotation', path_str = 'jj')
