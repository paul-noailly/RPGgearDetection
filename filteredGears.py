from classes.translator import Translator
from classes.gear import Gear, get_all_gears


class FilteredGears():
    def __init__(self, path_gears_data) -> None:
        self.path_gears_data = path_gears_data
        self.reset()
        
        self.translator = Translator()
        
    def reset(self):
        self.gears = get_all_gears(self.path_gears_data)
      
    
    def filter(self, **kwarg):
        """Potential arguments:
          - type: 'weapon', 'chest', 'speed', 'head', 'hands', 'neck'. Return all gears of type <type>
          - main_stat: atk, atk%, hp, hp%, def, def%, speed, cc, cd, focus, resi, agi, preci. Return all gears with main stat <main_stat>
          - level: int [1 - 15]. Return all gears with level above <level>
          - set: 'rage', 'vanguard', 'terra', 'raider', 'avarice', 'dragonscale', 'warrior', 'cursed', 'revival', 'raptor', 'assassin', 'faith', 'guard', 'divine', 'rebel'. Return all gears with set <set>
          - sub: atk, atk%, hp, hp%, def, def%, speed, cc, cd, focus, resi, agi, preci. Return all gears with at least a substat in <sub>
          - procs: int, return all gear with a number of procs above <proces>
          - ev: float, return all gears with a total efficient value above <ev>
          - ev_subs: float, return all gears with an total efficient value of procs above <ev_subs>
          - proc_quality: float, return all gears with an average efficient value of procs above <proc_quality>
          - rarity: legendary, epic, elite
        """
        for filter_tag, filter_value in kwarg.items():
          if filter_tag == 'type':
            self.gears = [gear for gear in self.gears if self.translator.translate_type(gear.type) == filter_value]
          elif filter_tag == 'main_stat':
            if '%' in filter_value or filter_value in ['cc', 'cd', 'resi', 'focus']:
              self.gears = sorted([gear for gear in self.gears if self.translator.translate_stat(gear.main_stat_name) == filter_value.replace('%','') and gear.main_stat_is_percent], key=lambda gear: -gear.main_stat_amount)
            else:
              self.gears = sorted([gear for gear in self.gears if self.translator.translate_stat(gear.main_stat_name) == filter_value and not gear.main_stat_is_percent], key=lambda gear: -gear.main_stat_amount)
          elif filter_tag == 'level':
            self.gears = sorted([gear for gear in self.gears if gear.level >= filter_value], key=lambda gear: -gear.level)
          elif filter_tag == 'set':
            self.gears = [gear for gear in self.gears if self.translator.translate_set(gear.set_name) == filter_value]
          # substats
          elif filter_tag == 'sub':
            if '%' in filter_value or filter_value in ['cc', 'cd', 'resi', 'focus']:
              self.gears = sorted([gear for gear in self.gears if filter_value.replace('%','') in [self.translator.translate_stat(substat.stat_name) for substat in gear.substats if substat.is_percent] ], key=lambda gear: -gear.get_sub_amount(filter_value))
            else:
              self.gears = sorted([gear for gear in self.gears if filter_value in [self.translator.translate_stat(substat.stat_name) for substat in gear.substats if not substat.is_percent] ], key=lambda gear: -gear.get_sub_amount(filter_value))
          elif filter_tag == 'procs':
            self.gears = sorted([gear for gear in self.gears if gear.total_procs == filter_value], key=lambda gear: -gear.total_procs)
          elif filter_tag == 'ev':
            self.gears = sorted([gear for gear in self.gears if gear.ev >= filter_value], key=lambda gear: -gear.ev)
          elif filter_tag == 'ev_subs':
            self.gears = sorted([gear for gear in self.gears if gear.ev_subs >= filter_value], key=lambda gear: -gear.ev_subs)
          elif filter_tag == 'proc_quality':
            self.gears = sorted([gear for gear in self.gears if gear.proc_quality >= filter_value], key=lambda gear: -gear.proc_quality)
          elif filter_tag == 'rarity':
            self.gears = [gear for gear in self.gears if self.translator.translate_set(gear.rarity) == filter_value]
        return self.gears