from gear import Gear, Substat
import json, unidecode

class InvalidGearException(Exception):
    pass

class MissmatchSubstatsException(Exception):
    pass

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
        self.texts = response.text_annotations
        #print('self.texts:')

        for text in self.texts:
            #print('\n"{}"'.format(text.description))

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices])

            #print('bounds: {}'.format(','.join(vertices)))

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
            
        return self.texts

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
    _TYPES = [
        "Arme",
        "Tête",
        "Buste",
        "Pieds",
        "Mains",
        "Cou"
    ]
    _STATS = [
        "Attaque",
        "Défense",
        "PV",
        "Taux",
        "Dégâts",
        "Vitesse",
        "Résistance",
        "Concentration",
        "Agilité",
        "Précision",
    ]
    _SETS = [
        'Guerrier', 
        'Fureur', 
        'Avant-Garde', 
        'Renaissance', 
        'Malédiction', 
        'Assassin', 
        'Divin',
        'Terre', 
        'Raid', 
        'Aigle', 
        'Foi', 
        'Draconique', 
        "l'Avarice", 
        'Garde', 
        'Invincibilité'
    ]
    _SUBS_NAME = "Stats"
    def __init__(self, folder_left, folder_substats):
        self.folder_left, self.folder_substats = folder_left, folder_substats

    def get_substats_amount(self, texts_substats):
        return [text.description for text in texts_substats][1:]

    def decode_level(self, texts_left):
        for i,text in enumerate(texts_left):
            if i == 1 and '+' in text.description:
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
                    is_similar_word, similar_word = match_word(text.description, Decoder._TYPES)
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
                    is_similar_word, similar_word = match_word(text.description, Decoder._STATS)
                    if is_similar_word:
                        self.mainStat = {
                            "raw": text.description,
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                            "value":similar_word
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
        raise InvalidGearException('Error - [subStart] not found')
    
    def decode_setPos(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.subStart['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] > self.subStart['coords_center'][1]:
                    if text.description == "Set":
                        self.setPos = {
                            "coords_center": center,
                            "coords_limit": limit_coords,
                            "index":i,
                        }
                        return True
        raise InvalidGearException('Error - [setPos] not found')
    
    def decode_setValue(self, texts_left):
        for i,text in enumerate(texts_left):
            if i > self.setPos['index']:
                center, limit_coords = get_coords(text.bounding_poly)
                if center[1] >= self.setPos['coords_limit']['min_y'] and center[1] <= self.setPos['coords_limit']['max_y']:
                    is_similar_word, similar_word = match_word(text.description, Decoder._SETS)
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
                    is_similar_word, similar_word = match_word(text.description, Decoder._STATS)
                    if is_similar_word:
                        self.substats[len(self.substats)] = {
                            "name": {
                                "raw": text.description,
                                "coords_center": center,
                                "coords_limit": limit_coords,
                                "index":i,
                                "value":similar_word
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
                    if '[' in text.description and ']' in text.description:
                        for substat_id, substat_dic in self.substats.items():
                            # print(text.description, center[1], substat_dic['name']['value'], substat_dic['name']['coords_limit']['min_y'], substat_dic['name']['coords_limit']['max_y'])
                            if center[1] >= substat_dic['name']['coords_limit']['min_y'] and center[1] <= substat_dic['name']['coords_limit']['max_y']:
                                self.substats[substat_id]['procs'] = {
                                    "raw": text.description,
                                    "coords_center": center,
                                    "coords_limit": limit_coords,
                                    "index":i,
                                    "value":int(text.description.replace('[','').replace(']','').replace('+','')) + 1
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
        main_stat_amount = float(self.mainStatValue['value'].replace('%',''))
        main_stat_is_percent = '%' in self.mainStatValue['value']
        set_name = self.setValue['value']
        substats = []

        for sub_id,sub_dict in self.substats.items():    
            stat_name = sub_dict['name']['value']
            if "procs" in sub_dict:
                nbs_procs = sub_dict['procs']['value']
            else:
                nbs_procs = 1
            if self.completed_substats:
                stat_amount = float(sub_dict['amount']['value'].replace('%',''))
                is_percent =  '%' in sub_dict['amount']['value']
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