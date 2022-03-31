from pynput import mouse
from PIL import ImageGrab
import sys

class MyException(Exception):pass


class ClickListener():
    def __init__(self):
        self.clicks = set()
        sys.tracebacklimit = 0
    
    def on_click(self, x, y, button, pressed):
        # print(x, y)
        self.clicks.add((x,y))
        # print(self.clicks, len(self.clicks))
        if len(self.clicks) >= 2:
            raise Exception("Finished calibration.")
            
    def take_screenshot(self, path, show=False):
        coords = sorted([coord for coord in self.clicks], key=lambda coord: coord[0])
        ss_region = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
        ss_img = ImageGrab.grab(ss_region)
        ss_img.save(path)
        self.last_img = ss_img
        
    def register_subspace(self):
        self.clicks = set()
        with mouse.Listener(on_click=self.on_click) as listener:
            try:
                listener.join()
            except Exception as e:
                pass
            