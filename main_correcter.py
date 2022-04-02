import time, datetime
from decoder import Decoder, InvalidGearException
import os, yaml, shutil, json
from gear import Gear, Substat
import unidecode

from PIL import Image   

def show_img(path):                                                                             
    img = Image.open(path)
    img.show()


def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    
config = yaml.safe_load(open("config.yaml","r"))
folder_left, folder_substats = config['folder_left'], config['folder_substats']
folder_result = config['folder_result']

gear_paths = [f'{folder_result}/{filename}' for filename in os.listdir(folder_result) if '.json' in filename]

incompleted_paths = [gear_path for gear_path in gear_paths if not json.load(open(gear_path, 'r'))['meta']['completed_substats']]
log(f"Incomplete gears: {len(incompleted_paths)}/{len(gear_paths)}")

for index_correction,gear_path in enumerate(incompleted_paths):
    
    with open(gear_path, 'r') as f:
        dict_gear = json.load(f)
        f.close()
        
    if not dict_gear['meta']['completed_substats']:
        print('...')
        log(f'Correcting {gear_path} - correction {index_correction}/{len(incompleted_paths)}')
        skip_this_correction = False
        stop_all_corrections = False
        while not skip_this_correction and not stop_all_corrections:
            decision = input('What do you want to do ?\nskip : skip this correction\nsub : Enter the substats value separated by a "-". Example "5-8%-365-7.5%" for 4 substats: [5, 8%, 365, 7.5%]\nshow : show picture of the substats values\nstop : stop the whole process\n>>')
            # skipping this correction
            if decision.lower() == "skip":
                break
            # entering the sub input
            elif "-" in decision.lower():
                subs_list = decision.replace(" ","").replace("sub","").split("-")
                confirm_subs = input(f'Do you confirm adding subs {subs_list} to gear n°{dict_gear["meta"]["index_img"]} ?  y/n\n>>')
                if confirm_subs.lower() == 'y':
                    print(f'Adding subs {decision} to gear n°{dict_gear["meta"]["index_img"]}')
                    # creating list of substats
                    substats = []
                    sub_dicts = dict_gear['substats']
                    for i,sub_value in enumerate(subs_list):
                        sub_dict = sub_dicts[i]
                        is_percent =  '%' in sub_value
                        stat_amount = float(sub_value.replace('%',''))
                        substats.append(Substat(stat_name=sub_dict['stat_name'], 
                                                stat_amount=stat_amount, 
                                                nbs_procs=sub_dict['nbs_procs'], 
                                                is_percent=is_percent))
                    # creating gear object
                    gear = Gear(
                        type = unidecode.unidecode(dict_gear['type']),
                        level = dict_gear['level'],
                        main_stat_name = dict_gear['main_stat_name'],
                        main_stat_amount = dict_gear['main_stat_amount'],
                        main_stat_is_percent = dict_gear['main_stat_is_percent'],
                        substats = substats,
                        set_name = dict_gear['set_name'],
                        meta = {"completed_substats":True, "index_img":dict_gear["meta"]["index_img"]})
                    # updating json dict of gear with new gear._asdict()
                    print(f"Updating gear dict: {gear._asdict()}")
                    with open(f"{folder_result}/{dict_gear['meta']['index_img']}.json","w+") as f:
                        json.dump(gear._asdict(), f)
                        f.close()
                    # breaking the loop to go to next gear to correct
                    break
                else:
                    print('Cancelling this subs input')
                    pass
            # showing image
            elif decision.lower() == "show":
                show_img(f"{folder_substats}/{dict_gear['meta']['index_img']}.png")
            # stopping the whole correction process
            elif decision.lower() == "stop":
                stop_all_corrections = True
                break
            else:
                pass
        if stop_all_corrections:
            log(f'Stopping all corrections')
            break
        
        