from unittest import case
from classes.gear import Gear, Substat
import json

def dict_to_stats(dic:dict):
    return Stats(
        atk=dic['atk'],
        hp=dic['hp'],
        defense=dic['defense'],
        speed=dic['speed'],
        cc=dic['cc'],
        cd=dic['cd'],
        focus=dic['focus'],
        res=dic['res'],
        agi=dic['agi'],
        preci=dic['preci']
    )

class Stats():
    def __init__(self, atk, hp, defense, speed, cc, cd, focus, res, agi, preci) -> None:
        self.atk, self.hp, self.defense, self.speed, self.cc, self.cd, self.focus, self.res, self.agi, self.preci = atk, hp, defense, speed, cc, cd, focus, res, agi, preci
        
        with open("data/translators/stat_names.json", "r") as f:
            self.stat_name_translator_dict = json.load(f)
            f.close()
        
    def _asdict(self):
        return {
            "atk": self.atk,
            "hp": self.hp,
            "defense": self.defense,
            "speed": self.speed,
            "cc": self.cc,
            "cd": self.cd,
            "focus": self.focus,
            "res": self.res,
            "agi": self.agi,
            "preci": self.preci,
        }
        
    def update(self, name, amount, is_percent):
        if is_percent and name not in ['cc', 'cd', 'focus', 'agi', 'resi', 'preci']:
            setattr(self, name, getattr(self, name) * (1+amount))
        else:
            setattr(self, name, getattr(self, name) + amount)
        
    def copy(self):
        return Stats(self.atk, self.hp, self.defense, self.speed, self.cc, self.cd, self.focus, self.res, self.agi, self.preci)
    
    def apply_gear(self, gear:Gear):
        print(f"Before equiping gear stats = {self._asdict()}")
        # apply main stat
        self.update(gear.main_stat_name, gear.main_stat_amount, gear.main_stat_is_percent)
        # apply sub stats
        for substat in gear.substats:
            stat_name = self.stat_name_translator_dict[substat.stat_name]
            self.update(stat_name, substat.stat_amount, substat.is_percent)        
        # register set name
        
        # end
        print(f"Atfer equiping gear stats = {self._asdict()}")
        