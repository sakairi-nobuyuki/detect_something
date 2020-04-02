import os
import glob
import shutil
import xmltodict
import json
import xml.etree.ElementTree as ET


def load_correct_data (correct_data_dir_path, path_str = None):
    #import xml.etree.ElementTree as ET

    if path_str == 'jj':
        xml_path_list = glob.glob ('../{}/*/*/*/*.xml'.format (correct_data_dir_path), recursive = True)
        print (xml_path_list)
        for xml_path in xml_path_list:
     #       tree = ET.parse (xml_path) 
     #       for item in tree.iter ():
     #           print ("item tag", item.tag)
     #           print ("item atr", item.attrib)
     #           print ("item txt", item.text)
        exit ()


if __name__ == '__main__':
    ### bouding_box = [n_bb, x1, y1, x2, y2, label]
    load_correct_data ('annotation', path_str = 'jj')
