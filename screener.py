from clickListener import ClickListener
from PIL import Image
import os

class Screener():
    def  __init__(self, folder_img) -> None:
        self.clickListener = ClickListener()
        self.index = 0
        self.folder_img = folder_img
        
    def delete_screenshot_if_redonant(self):
        if self.index >= 2:
            is_identical = (Image.open(f'{self.folder_img}/{self.index}.png').__array__()==Image.open(f'{self.folder_img}/{self.index-1}.png').__array__()).all()
            if is_identical:
                os.remove(f'{self.index}.png')
                print("redondant screenshot. DELETED")
            else:
                self.index += 1
        else:
            self.index += 1
    
    def run_calibration(self):
        self.clickListener.register_subspace()

    def screenshot(self, path="test.png"):
        self.clickListener.take_screenshot(path)