import time, datetime
from screener import Screener
import os, yaml



        
def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    

config = yaml.safe_load(open("config.yaml","r"))
folder_left = config['folder_left']
folder_substats = config['folder_substats']
sec_between_screenshot = config['sec_between_screenshot']

# make dirs
for folder in [folder_left, folder_substats]:
    try:
        os.makedirs(folder)
    except:
        pass

if __name__ == '__main__':
    bot = Screener(folder_left, folder_substats)
    log('Calibrate screen left')
    bot.run_calibration_left()    
    time.sleep(1)
    log('Calibrate screen substats')
    bot.run_calibration_substats()
    log('Calibration is done, starting screenshoting...')
    print()
    while True:
        log(f'taking screenshot n°{bot.index}...')
        bot.screenshot(f"{bot.index}.png")
        bot.delete_screenshot_if_redonant()
        log('done.')
        print()
        time.sleep(sec_between_screenshot)