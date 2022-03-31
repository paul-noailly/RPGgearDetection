from clickListener import ClickListener
from PIL import Image
import os


class Screener():
    def  __init__(self, folder_img_left, folder_img_substats) -> None:
        self.clickListener = ClickListener()
        self.index = 0
        self.folder_img_left = folder_img_left
        self.folder_img_substats = folder_img_substats
        
    def delete_screenshot_if_redonant(self):
        if self.index >= 2:
            is_identical_left = (Image.open(f'{self.folder_img_left}/{self.index}.png').__array__()==Image.open(f'{self.folder_img_left}/{self.index-1}.png').__array__()).all()
            is_identical_substats = (Image.open(f'{self.folder_img_substats}/{self.index}.png').__array__()==Image.open(f'{self.folder_img_substats}/{self.index-1}.png').__array__()).all()
            if is_identical_left and is_identical_substats:
                os.remove(f'{self.folder_img_left}/{self.index}.png')
                os.remove(f'{self.folder_img_substats}/{self.index}.png')
                print("redondant screenshot. DELETED")
            else:
                self.index += 1
        else:
            self.index += 1
    
    def run_calibration_substats(self):
        self.clickListener.register_subspace_substats()
        
    def run_calibration_left(self):
        self.clickListener.register_subspace_left()

    def screenshot(self, filename="test.png"):
        print('Left screnshot')
        self.clickListener.take_screenshot_left(f"{self.folder_img_left}/{filename}")
        print('substats screenshot')
        self.clickListener.take_screenshot_substats(f"{self.folder_img_substats}/{filename}")