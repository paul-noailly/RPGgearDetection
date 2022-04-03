def dict_to_ascends(dic:dict):
    return Ascends(dic[0], dic[1], dic[2], dic[3], dic[4])

class Ascends():
    hp = {"hp": 0.15}
    atk = {"atk": 0.15}
    speed = {"speed": 15}
    defense = {"defense": 0.15}
    trait = {}
    def __init__(self, bonus1, bonus2, bonus3, bonus4, bonus5, bonus6={"hp":0.05, "atk":0.05, "defense":0.05}) -> None:
        self.bonuses = [bonus1, bonus2, bonus3, bonus4, bonus5, bonus6]
        
    def apply_bonuses(self, stats, nbs_ascends):
        if nbs_ascends == 6:
            stats['hp'] *= 1.2
            stats['atk'] *= 1.2
            stats['speed'] += 15
            stats['defense'] *= 1.2
        else:
            for i in range(0,nbs_ascends-1):
                for k,v in self.bonuses[i].items():
                    if k == "speed":
                        stats[k] += v
                    else:
                        stats[k] *= (1+v)
        return stats
                    
    def remove_all_bonuses(self, stats):
            stats['hp'] /= 1.2
            stats['atk'] /= 1.2
            stats['speed'] -= 15
            stats['defense'] /= 1.2
            return stats
        
        
    def _asdict(self):
        return {i:self.bonuses[i] for i in range(len(self.bonuses))}