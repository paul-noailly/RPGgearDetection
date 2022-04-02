import json
import unidecode

def stat_to_ev(name, value, is_percent, ev_dict=json.load(open('data/ev_dict_fr_6star.json','r'))):
    try:
        if is_percent:
            return float(value) / ev_dict['percent'][name]
        else:
            return float(value) / ev_dict['fix'][name]
    except:
        return 0
    

class Substat():
    def __init__(self, stat_name, stat_amount, nbs_procs, is_percent):
        self.stat_name = stat_name
        self.stat_amount = stat_amount
        self.nbs_procs = nbs_procs
        self.is_percent = is_percent
        
    def get_ev(self, ev_dict=json.load(open('data/ev_dict_fr_6star.json','r'))):
        return stat_to_ev(self.stat_name, self.stat_amount, self.is_percent, ev_dict)
    
    def _asdict(self):
        return {
            "stat_name": unidecode.unidecode(self.stat_name),
            "stat_amount": self.stat_amount,
            "nbs_procs": self.nbs_procs,
            "is_percent": self.is_percent,
        }

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
        
        self.ev_subs = self.get_ev_subs()
        self.ev = self.get_ev()
        self.total_procs = sum([substat.nbs_procs for substat in self.substats])
        self.proc_quality = self.ev_subs / self.total_procs
        self.initial_procs = self.total_procs - self.level // 3
        if self.initial_procs in [2,3,4]:
            self.rarity = {2:"elite",3:"epic",4:"legendary"}[self.initial_procs]  
        else:
            self.rarity = "unknown"
        
        print([substat._asdict() for substat in self.substats])
        
    def get_ev_subs(self):
        ev_dict = json.load(open('data/ev_dict_fr_6star.json','r'))
        total_ev = 0
        for substat in self.substats:
            total_ev += substat.get_ev(ev_dict)
        return total_ev
    
    def get_ev(self):
        ev_dict = json.load(open('data/ev_dict_fr_6star.json','r'))
        return stat_to_ev(self.main_stat_name, self.main_stat_amount, self.main_stat_is_percent, ev_dict) + self.ev_subs
    
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