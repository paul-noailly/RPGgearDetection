import time, datetime
from decoder import Decoder
import os, yaml



        
def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    

config = yaml.safe_load(open("config.yaml","r"))
folder_json = config['folder_json1']
folder_img = config['folder_img']

# make dirs
try:
    os.makedirs(folder_json)
except:
    pass

if __name__ == '__main__':
    bot = Decoder(folder_json)
    paths = [f"{folder_img}/{filename}" for filename in os.listdir(folder_img) if ".png" in filename]
    print(paths)
    log(f"Preparing {len(paths)} images to decode...")
    for path in paths:
        if path in [f"img/{index}.png" for index in [16,6,2,15]] or False:
            print()
            log(f"decoding {path} ...")
            bot.decode(path)