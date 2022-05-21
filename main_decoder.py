import time, datetime
from decoder import Decoder, InvalidGearException
import os, yaml, shutil, json

def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    
config = yaml.safe_load(open("config.yaml","r"))
folder_left, folder_substats = config['folder_left'], config['folder_substats']
folder_result = config['folder_result']
language = config['language']

# make dirs
if os.path.exists(folder_result):
    shutil.rmtree(folder_result)
os.makedirs(folder_result)
  

if __name__ == '__main__':
    from decoder import Decoder
    bot = Decoder(folder_left, folder_substats, language)
    indices = [int(filename.replace('.png','')) for filename in os.listdir(folder_left) if ".png" in filename]
    log(f"Preparing {len(indices)} images to decode...")
    indices_to_correct = []
    
    # decode all gear
    for index in indices:
        print()
        log(f"decoding n°{index} ...")
        try:
            dict_gear = bot.decode(index)
            with open(f"{folder_result}/{index}.json","w+") as f:
                json.dump(dict_gear, f)
                f.close()
            if not dict_gear['meta']['completed_substats']: # there is missmatch between detected sub values and sub names
                indices_to_correct.append(index)
        except InvalidGearException as e: # the gear is invalid
            log(f"img n°{index} is invalid because of: {e}")
            
    # correct missmatchs
    log(f"Found {len(indices_to_correct)} missmatches to correct")
            
        
        
    