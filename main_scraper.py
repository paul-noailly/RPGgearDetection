import time, datetime
from screener import Screener
import os, yaml



        
def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    

config = yaml.safe_load(open("config.yaml","r"))
folder_img = config['folder_img']
sec_between_screenshot = config['sec_between_screenshot']

# make dirs
try:
    os.makedirs(folder_img)
except:
    pass

if __name__ == '__main__':
    bot = Screener(folder_img)
    log('Calibrate screen')
    bot.run_calibration()
    log('Calibration is done, starting screenshoting...')
    print()
    while True:
        log(f'taking screenshot n°{bot.index}...')
        bot.screenshot(f"{folder_img}/{bot.index}.png")
        bot.delete_screenshot_if_redonant()
        log('done.')
        print()
        time.sleep(sec_between_screenshot)