import json

class Translator():
    def __init__(self):
        folder_translations_data = "data/translators"
        # import type translations
        with open(f"{folder_translations_data}/type_names.json", "r") as f:
            self.translations_type_names = json.load(f)
            f.close()
        # import stat translations
        with open(f"{folder_translations_data}/stat_names.json", "r") as f:
            self.translations_stat_names = json.load(f)
            f.close()
        # import set translations
        with open(f"{folder_translations_data}/set_names.json", "r") as f:
            self.translations_set_names = json.load(f)
            f.close()
        # import rarity translations
        with open(f"{folder_translations_data}/rarity_names.json", "r") as f:
            self.translations_rarity_names = json.load(f)
            f.close()
    
    def translate_type(self, value):
        return self.translations_type_names[value]
    
    def translate_set(self, value):
        return self.translations_set_names[value]
    
    def translate_stat(self, value):
        return self.translations_stat_names[value]
    
    def translate_rarity(self, value):
        return self.translations_rarity_names[value]