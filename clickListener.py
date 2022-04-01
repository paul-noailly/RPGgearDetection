from pynput import mouse
from PIL import ImageGrab
import sys

class MyException(Exception):pass


class ClickListener():
    def __init__(self):
        self.clicks_left = set()
        self.clicks_substats = set()
        sys.tracebacklimit = 0
    
    def on_click_substats(self, x, y, button, pressed):
        # print(x, y)
        self.clicks_substats.add((x,y))
        # print(self.clicks, len(self.clicks))
        if len(self.clicks_substats) >= 2:
            raise Exception("Finished calibration.")
        
    def on_click_left(self, x, y, button, pressed):
        # print(x, y)
        self.clicks_left.add((x,y))
        # print(self.clicks, len(self.clicks))
        if len(self.clicks_left) >= 2:
            raise Exception("Finished calibration.")
            
    def take_screenshot_left(self, path, show=False):
        coords = sorted([coord for coord in self.clicks_left], key=lambda coord: coord[0])
        ss_region = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
        ss_img = ImageGrab.grab(ss_region)
        ss_img.save(path)
        self.last_img = ss_img
        
    def take_screenshot_substats(self, path, show=False):
        coords = sorted([coord for coord in self.clicks_substats], key=lambda coord: coord[0])
        ss_region = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
        ss_img = ImageGrab.grab(ss_region)
        ss_img.save(path)
        self.last_img = ss_img
        
    def register_subspace_substats(self):
        self.clicks_substats = set()
        with mouse.Listener(on_click=self.on_click_substats) as listener:
            try:
                listener.join()
            except Exception as e:
                pass
        print(self.clicks_substats)
            
    def register_subspace_left(self):
        self.clicks_left = set()
        with mouse.Listener(on_click=self.on_click_left) as listener:
            try:
                listener.join()
            except Exception as e:
                pass
        print(self.clicks_left)
            