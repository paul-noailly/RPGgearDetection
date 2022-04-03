import json, os
import unidecode
from classes.translator import Translator

def stat_to_ev(name, value, is_percent, translator, ev_dict):
    try:
        if is_percent:
            return float(value) / ev_dict['percent'][translator.translate_stat(name)]
        else:
            return float(value) / ev_dict['fix'][translator.translate_stat(name)]
    except Exception as e:
        return 0
    
def dict_to_substat(dic:dict):
    return Substat(
        stat_name = dic["stat_name"],
        stat_amount = dic["stat_amount"],
        nbs_procs = dic["nbs_procs"],
        is_percent = dic["is_percent"],
    )
    
def get_all_gears(path_gears_data):
    paths = [f"{path_gears_data}/{filename}" for filename in os.listdir(path_gears_data)]
    gears = []
    for path in paths:
        with open(path,"r") as f:
            gears.append(dict_to_gears(json.load(f)))
            f.close()
    return gears

class Substat():
    def __init__(self, stat_name, stat_amount, nbs_procs, is_percent):
        self.stat_name = stat_name
        self.stat_amount = stat_amount
        self.nbs_procs = nbs_procs
        self.is_percent = is_percent
        
        
    def get_ev(self, translator, ev_dict):
        return stat_to_ev(self.stat_name, self.stat_amount/self.nbs_procs, self.is_percent, translator, ev_dict)
    
    def _asdict(self):
        return {
            "stat_name": unidecode.unidecode(self.stat_name),
            "stat_amount": self.stat_amount,
            "nbs_procs": self.nbs_procs,
            "is_percent": self.is_percent,
        }
        
    def __str__(self):
        percent = {True:"%",False:""}[self.is_percent]
        return f"{self.stat_name}[+{self.nbs_procs}](+{self.stat_amount}{percent})"
        
def dict_to_gears(dic:dict):
    return Gear(        
        type = dic['type'],
        level = dic['level'],
        main_stat_name = dic['main_stat_name'],
        main_stat_amount = dic['main_stat_amount'],
        main_stat_is_percent = dic['main_stat_is_percent'],
        substats = [dict_to_substat(dic_substat) for dic_substat in dic['substats']],
        set_name = dic['set_name'],
        meta = dic['meta']
    )

class Gear():
    def __init__(self, type, level, main_stat_name, main_stat_amount, main_stat_is_percent, substats, set_name, meta):
        self.type = type
        self.level = level
        self.main_stat_name = main_stat_name
        self.main_stat_amount = main_stat_amount
        self.main_stat_is_percent = main_stat_is_percent
        self.substats = substats
        self.set_name = set_name
        self.meta = meta
        
        self._translator = Translator()
        
        self.ev_subs = self.get_ev_subs()
        self.ev = self.get_ev()
        self.total_procs = sum([substat.nbs_procs for substat in self.substats])
        self.proc_quality = self.get_proc_quality()
        self.initial_procs = self.total_procs - self.level // 3
        if self.initial_procs in [2,3,4]:
            self.rarity = {2:"elite",3:"epic",4:"legendary"}[self.initial_procs]  
        else:
            self.rarity = "unknown"
        
        #print([substat._asdict() for substat in self.substats])
        
    def get_ev_subs(self):
        ev_dict = json.load(open('data/ev/ev_dict_fr_6star.json','r'))
        total_ev = 0
        for substat in self.substats:
            total_ev += substat.get_ev(self._translator, ev_dict)
        return total_ev
    
    def get_proc_quality(self):
        ev_dict = json.load(open('data/ev/ev_dict_fr_6star.json','r'))
        total_ev = 0
        for substat in self.substats:
            total_ev += substat.get_ev(self._translator, ev_dict) * substat.nbs_procs
        return total_ev / self.total_procs
    
    def get_ev(self):
        ev_dict = json.load(open('data/ev/ev_dict_fr_6star.json','r'))
        return stat_to_ev(self.main_stat_name, self.main_stat_amount, self.main_stat_is_percent, self._translator, ev_dict) + self.ev_subs
    
    def get_sub_amount(self, stat_name):
        if "%" in stat_name or stat_name in ['cc', 'cd', 'resi', 'focus']:
            for substat in self.substats:
                if self._translator.translate_stat(substat.stat_name) == stat_name.replace('%','') and substat.is_percent:
                    return substat.stat_amount
            raise Exception(f'Error {stat_name} not in {str(self)}')
        
        else:
            for substat in self.substats:
                if self._translator.translate_stat(substat.stat_name) == stat_name and not substat.is_percent:
                    return substat.stat_amount
            raise Exception(f'Error {stat_name} not in {str(self)}')
    
    def _asdict(self):
        return {
            "type": self.type,
            "level": self.level,
            "rarity": self.rarity,
            "main_stat_name": unidecode.unidecode(self.main_stat_name),
            "main_stat_amount": self.main_stat_amount,
            "main_stat_is_percent": self.main_stat_is_percent,
            "set_name": unidecode.unidecode(self.set_name),
            "substats": [substat._asdict() for substat in self.substats],
            "quality": {
                "ev": self.ev,
                "proc_quality": self.proc_quality,
                "total_procs": self.total_procs,
                "initial_procs": self.initial_procs           
            },
            "meta": self.meta
        }
        
    def __str__(self):
        percent = {True:"%",False:""}[self.main_stat_is_percent]
        substats_str = "|".join([str(substat) for substat in self.substats])
        return f"{self.type}[+{self.level}] {self.set_name} - {self.main_stat_name} +{self.main_stat_amount}{percent} procs_ev={round(self.proc_quality,2)} Subs:{substats_str}"