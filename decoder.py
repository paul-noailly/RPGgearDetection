from gear import Gear, Substat
import json, unidecode

class InvalidGearException(Exception):
    pass

class MissmatchSubstatsException(Exception):
    pass

def mergeVertices(source, extension):
    source.bounding_poly.vertices[1].x = extension.bounding_poly.vertices[1].x
    source.bounding_poly.vertices[2].x = extension.bounding_poly.vertices[2].x
    source.bounding_poly.vertices[2].y = extension.bounding_poly.vertices[2].y
    source.bounding_poly.vertices[3].y = extension.bounding_poly.vertices[3].y

# Comparator accepting an imprecision of 2px
def vertices_compare(i1, i2):
    return i1[0] < i2[0] if abs(i2[1] - i1[1]) <= 2 else i1[1] < i2[1]

# Sort values by adding one at time
def sort_values(d):
    sorted_list = []
    for key,_ in d.items():
        ind_to_insert = 0
        for ind, value in enumerate(sorted_list):
            if vertices_compare(key, value) == False:
                ind_to_insert = ind + 1
            else:
                break
        sorted_list.insert(ind_to_insert, key)
    return sorted_list


class OCR():
    def __init__(self) -> None:
        pass
    
    def detect_text(self, path):
        """Detects text in the file."""
        from google.cloud import vision
        import io
        client = vision.ImageAnnotatorClient.from_service_account_json('service-account-file.json')

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        #print("texts=" + str([b.description for b in texts]))
        #print('texts:')

        # for text in texts:
        #    #print('\n"{}"'.format(text.description))

        #    vertices = (['({},{})'.format(vertex.x, vertex.y)
        #                for vertex in text.bounding_poly.vertices])

        #    #print('bounds: {}'.format(','.join(vertices)))

        # Rework the text returned from the text_detection() function to help the extraction
        values = [ texts[0] ]
        passNb = 0
        for ind, text in enumerate(texts[1:]):
            if passNb > 0:
                passNb -= 1
                continue
            if text.description == "%":
                values[-1].description += "%"
                mergeVertices(values[-1], text)
            elif text.description == "Taux":
                text.description += " de Crit."
                mergeVertices(text, texts[ind + 4])
                values.append(text)
                passNb = 3
            elif text.description == "Dégâts" or text.description == "Dégats" or \
                 text.description == "Degâts" or text.description == "Degats":
                text.description += " de Crit."
                mergeVertices(text, texts[ind + 4])
                values.append(text)
                passNb = 3
            elif text.description == "Crit" and (texts[0].description.find("Crit. Rate") != -1 or
                                                 texts[0].description.find("Crit. Damage") != -1):
                text.description += ". " + texts[ind + 3].description
                mergeVertices(text, texts[ind + 3])
                values.append(text)
                passNb = 2
            elif text.description == "[" and '+' in texts[ind + 2].description and texts[ind + 3].description == "]":
                text.description += texts[ind + 2].description + "]"
                mergeVertices(text, texts[ind + 3])
                values.append(text)
                passNb = 2
            else:
                values.append(text)

        # Correction of the text order defined by the center of each text rectangle
        valuesByCenter = {}
        for v in values[1:]:
            valuesByCenter[((v.bounding_poly.vertices[0].x + v.bounding_poly.vertices[2].x)/2,
                            (v.bounding_poly.vertices[0].y + v.bounding_poly.vertices[2].y)/2)] = v
        sorted_keys = sort_values(valuesByCenter)
        values = [ values[0] ]
        for key in sorted_keys:
            values.append(valuesByCenter[key])

        #print("values=" + str([b.description for b in values]))
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
            
        return values

def get_coords(bounding_poly):
    coords = []
    for i in range(0,4):
        coords.append((bounding_poly.vertices[i].x, bounding_poly.vertices[i].y))
    center = ((max(coords)[0] + min(coords)[0])/2, (max(coords)[1] + min(coords)[1])/2)
    limit_coords = {
        'min_x':min(coords)[0],
        'min_y':min(coords)[1],
        'max_x':max(coords)[0],
        'max_y':max(coords)[1]
        }
    return center, limit_coords

def match_word(target, words_to_check):
    for similar_word in words_to_check:
        # print('comparing',target,similar_word)
        # check excact same
        if target.lower() == similar_word.lower():
            return True, similar_word
    return False, None


def is_str_of_float(target):
    try:
        float(target.replace('%',''))
        return True
    except:
        return False


class Decoder():
    _SUBS_NAME = "Stats"

    def __init__(self, folder_left, folder_substats, language):
        self.folder_left     = folder_left
        self.folder_substats = folder_substats
        self.language        = language

        if self.language == "fr":
            self.TYPES = ["Arme", "Tête", "Buste", "Pieds", "Mains", "Cou"]
            self.STATS = ["Attaque", "Défense", "PV", "Taux de Crit.", "Dégâts de Crit.", "Vitesse", "Résistance", "Concentration", "Agilité", "Précision"]
            self.SETS =  ["Guerrier", "Fureur", "d'Avant-Garde", "Renaissance", "Malédiction", "d'Assassin", "Divin",
                          "Terre", "Raid", "d'Aigle", "Foi", "Draconique", "l'Avarice", "Garde", "d'Invincibilité"]
        else: # "en"
            self.TYPES = ["Weapon", "Head", "Chest", "Feet", "Hands", "Neck"]
            self.STATS = ["Attack", "Health", "Defense", "Speed", "Crit. Rate", "Crit. Damage", "Focus", "Resistance", "Agility", "Precision"]
            self.SETS =  ["Warrior", "Rage", "Vanguard", "Revival", "Cursed", "Assassin", "Divine", "Terra",
                          "Raider", "Raptor", "Faith", "Dragonscale", "Avarice", "Guard", "Rebel"]

    def get_substats_amount(self, texts_substats):
        return [text.description for text in texts_substats][1:]

    def decode_level(self, texts_left):
        for i,text in enumerate(texts_left):
            if i >= 1 and '+' in text.description:
                center, limit_coords = get_coords(text.bounding_poly)
                self.level = {
                    "raw": text.description,
                    "coords_center": center,
                    "coords_limit": limit_coords,
                    "index":i,
                    "value":int(text.description[1:])
                }
                return True
        raise InvalidGearException('Error - [level] not found')

    def decode_type(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.level['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.level['coords_center'][1]:
                    is_similar_word, similar_word = match_word(text.description, self.TYPES)
                    if is_similar_word:
                        self.type = {
                            "raw": text.description,
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                            "value":similar_word
                        }
                        return True
        raise InvalidGearException('Error - [type] not found')
    
    def decode_mainStat(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.type['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.type['coords_center'][1]:
                    is_similar_word, similar_word = match_word(text.description, self.STATS)
                    if is_similar_word:
                        self.mainStat = {
                            "raw": text.description,
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                            "value":similar_word.replace("Taux de Crit.", "Taux").replace("Dégâts de Crit.", "Dégâts")
                        }
                        return True
        raise InvalidGearException('Error - [mainStat] not found')
    
    def decode_subStart(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.mainStat['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.mainStat['coords_center'][1]:
                    if text.description == Decoder._SUBS_NAME: # Stats
                        self.subStart = {
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                        }
                        return True
        raise InvalidGearException('Error - [subStart] not found')
        
    def decode_mainStatValue(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.mainStat['index'] and i < self.subStart['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.mainStat['coords_center'][1] and center[1] < self.subStart['coords_center'][1]:
                    if is_str_of_float(text.description) and text.description != "0":
                        self.mainStatValue = {
                            "raw": text.description,
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                            "value":text.description
                        }
                        return True
        raise InvalidGearException('Error - [mainStatValue] not found')
    
    def decode_setPos(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.subStart['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.subStart['coords_center'][1]:
                    if text.description == "Set":
                        self.setPos = {
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index": i - (1 if self.language == "en" else 0),
                        }
                        return True
        raise InvalidGearException('Error - [setPos] not found')
    
    def decode_setValue(self, texts_left):
        for i,text in enumerate(texts_left):
            if i >= self.setPos['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] >= self.setPos['coords_limit']['min_y'] and center[1] <= self.setPos['coords_limit']['max_y']:
                    is_similar_word, similar_word = match_word(text.description, self.SETS)
                    if is_similar_word:
                        self.setValue = {
                            "raw": text.description,
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                            "value":similar_word
                        }
                        return True
        raise InvalidGearException('Error - [setValue] not found')
    
    
    def decode_substatsName(self, texts_left):
        self.substats = {}
        for i,text in enumerate(texts_left):
            if i > self.subStart['index'] and i < self.setPos['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] >= self.subStart['coords_center'][1] and center[1] <= self.setPos['coords_center'][1]:
                    is_similar_word, similar_word = match_word(text.description, self.STATS)
                    if is_similar_word:
                        self.substats[len(self.substats)] = {
                            "name": {
                                "raw": text.description,
                                "coords_center": center,
                                "coords_limit": limit_coords,
                                "index":i,
                                "value":similar_word.split()[0]
                            }
                        }
                    if len(self.substats) >= 4:
                        return True
        return True
        # raise InvalidGearException('Error - [substatsName] not found')
    
    def decode_substatsProcs(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.subStart['index'] and i < self.setPos['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] >= self.subStart['coords_center'][1] and center[1] <= self.setPos['coords_center'][1]:
                    if text.description.startswith("[+") and text.description.endswith("]"):
                        for substat_id, substat_dic in self.substats.items():
                            # print(text.description, center[1], substat_dic['name']['value'], substat_dic['name']['coords_limit']['min_y'], substat_dic['name']['coords_limit']['max_y'])
                            if center[1] >= substat_dic['name']['coords_limit']['min_y'] and center[1] <= substat_dic['name']['coords_limit']['max_y']:
                                self.substats[substat_id]['procs'] = {
                                    "raw": text.description,
                                    "coords_center": center,
                                    "coords_limit": limit_coords,
                                    "index":i,
                                    "value":int(text.description[2]) + 1
                                }
                                break
    
    
    def decode_substatsAmount(self, texts_substats):
        substats_amount = self.get_substats_amount(texts_substats)
        if len(substats_amount) != len(self.substats):
            self.completed_substats = False
            print('Error - in [substatsAmount] missmatch with length substats')
        else:
            for substat_id, substat_dic in self.substats.items():
                self.completed_substats = True
                self.substats[substat_id]['amount'] = {
                                        "raw": substats_amount[substat_id],
                                        "value": substats_amount[substat_id]
                                    } 
        
    def decode(self, index):
        path_left = f"{self.folder_left}/{index}.png"
        path_substats = f"{self.folder_substats}/{index}.png"

        ocr = OCR()
        texts_substats = ocr.detect_text(path_substats)
        texts_left = ocr.detect_text(path_left)
        
        
        self.decode_level(texts_left)
        self.get_substats_amount(texts_substats)
        self.decode_type(texts_left)
        self.decode_mainStat(texts_left)
        self.decode_subStart(texts_left)
        self.decode_mainStatValue(texts_left)
        self.decode_setPos(texts_left)
        self.decode_setValue(texts_left)
        self.decode_substatsName(texts_left)
        self.decode_substatsProcs(texts_left)
        self.decode_substatsAmount(texts_substats)
        
        type = self.type['value']
        level = self.level['value']
        main_stat_name = self.mainStat['value']
        main_stat_amount = float(self.mainStatValue['value'].replace('%','').replace('°','').replace(',','').replace(' ','').replace('-',''))
        main_stat_is_percent = '%' in self.mainStatValue['value'] or "°" in self.mainStatValue['value'] or "," in self.mainStatValue['value'] or "-" in self.mainStatValue['value']
        set_name = self.setValue['value']
        substats = []

        for sub_id,sub_dict in self.substats.items():    
            stat_name = sub_dict['name']['value']
            if "procs" in sub_dict:
                nbs_procs = sub_dict['procs']['value']
            else:
                nbs_procs = 1
            if self.completed_substats:
                try:
                    stat_amount = float(sub_dict['amount']['value'].replace('%','').replace('°','').replace(',','').replace(' ','').replace('-',''))
                except ValueError:
                    stat_amount = 0
                is_percent =  '%' in sub_dict['amount']['value'] or "°" in sub_dict['amount']['value'] or "," in sub_dict['amount']['value'] or "-" in sub_dict['amount']['value']
            else:
                stat_amount = 0
                is_percent = False
            substats.append(Substat(stat_name=stat_name, stat_amount=stat_amount, nbs_procs=nbs_procs, is_percent=is_percent))


        gear = Gear(
            type = unidecode.unidecode(type),
            level = level,
            main_stat_name = main_stat_name,
            main_stat_amount = main_stat_amount,
            main_stat_is_percent = main_stat_is_percent,
            substats = substats,
            set_name = set_name,
            meta = {"completed_substats":self.completed_substats, "index_img":index})
        
        return gear._asdict()