from typing import List
from gear import Gear, Substat
from stats import Stats, dict_to_stats
from ascends import Ascends, dict_to_ascends
import json
        
def dict_to_hero(dic:dict):
    return Hero(
        name=dic['name'],
        element=dic['element'],
        rarity=dic['rarity'],
        base_stats=dict_to_stats(dic['base_stats']),
        ascends=dict_to_ascends(dic['ascends'])
        )
      
class Hero():
    def __init__(self, name:str, element:str, rarity:str,  base_stats:Stats, ascends:Ascends) -> None:
        self.name = name
        self.element = element
        self.rarity = rarity
        self.base_stats = base_stats
        self.ascends = ascends
    
    def _asdict(self):
        return {
            "name": self.name,
            "element": self.element,
            "rarity": self.rarity,
            "base_stats": self.base_stats._asdict(),
            "ascends": self.ascends._asdict()
        }
        
    def save_json(self, path):
        with open(path,'w+') as f:
            json.dump(self._asdict(), f)
            f.close()
    
    def get_current_stats(self, nbs_ascend, gears):
        base_ascended_stats = self.apply_bonuses(self.ascends.remove_all_bonuses(self.base_stats), nbs_ascend)
        stats = base_ascended_stats.copy()
        for gear_type,gear in gears.items():
            stats.apply_gear(gear)
        return stats