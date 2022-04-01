import time, datetime
from decoder import Decoder, InvalidGearException
import os, yaml, shutil, json

from PIL import Image   

def show_img(path):                                                                             
    img = Image.open('test.png')
    img.show()


def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    
config = yaml.safe_load(open("config.yaml","r"))
folder_left, folder_substats = config['folder_left'], config['folder_substats']
folder_result = config['folder_result']

gear_paths = [f'{folder_result}/{filename}' for filename in os.listdir(folder_result) if '.json' in filename]

for gear_path in gear_paths:
    
    with open(gear_path, 'r') as f:
        dict_gear = json.load(f)
        f.close()
        
    if not dict_gear['meta']['completed_substats']:
        print('...')
        log(f'Correcting {gear_path}')
        allow_correction = input('Correct this gear ? y/n')
        if allow_correction.lower() == 'y':
            show_img(f"{folder_substats}/{dict_gear['meta']['index_img']}.png")
        else:
            pass