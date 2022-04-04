import os, json, datetime, yaml, shutil


def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    
config = yaml.safe_load(open("config.yaml","r"))
folder_left, folder_substats = config['folder_left'], config['folder_substats']
folder_result = config['folder_result']
folder_result_merged = config['folder_result_merged']


try:
    os.makedirs(folder_result_merged)
except:
    shutil.rmtree(folder_result_merged)
    os.makedirs(folder_result_merged)

if __name__ == '__main__':
    paths = [f"{folder_result}/{filename}" for filename in os.listdir(folder_result) if ".json" in filename]
    
    merged_dict = {}
    for path in paths:
        with open(path, "r") as f:
            gear_dict = json.load(f)
            f.close()
        merged_dict[gear_dict['meta']['index_img']] = gear_dict
        
    print(f"Adding {len(merged_dict)} gears dict to the merged json")
    
    with open(f"{folder_result_merged}/gears.json", "w+") as f:
        json.dump(merged_dict, f)
        f.close()
    