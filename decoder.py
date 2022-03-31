import json, datetime, yaml

def log(msg):
    print(f"[{datetime.datetime.now()}] - {msg}")
    
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

class Decoder():
    _TYPES = ['arme', 'buste', 'tête', 'pieds', 'mains', 'cou']
    _STATS = ['Attaque', 'Défense', 'PV', 'Vitesse', 'Concentration', 
                 'Résistance', 'Taux', 'Précision', 'Dégâts', 'Agilité']
    _SETS = ['Guerrier', 
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
             'Invincibilité']
    def __init__(self, folder_json):
        self.folder_json = folder_json
        
    def get_coords(self, text):
        coords = []
        for i in range(0,4):
            coords.append((text.bounding_poly.vertices[i].x, text.bounding_poly.vertices[i].y))
        center = ((max(coords)[0] + min(coords)[0])/2, (max(coords)[1] + min(coords)[1])/2)
        limit_coords = {
            'min_x':min(coords)[0],
            'min_y':min(coords)[1],
            'max_x':max(coords)[0],
            'max_y':max(coords)[1]
            }
        return coords, center, limit_coords
    
    def description_is_a_type(self, word_given):
        for word_to_guess in Decoder._TYPES:
            letters_in_common = set()
            for letter in word_given:
                if letter in word_to_guess:
                    letters_in_common.add(letter)
            if len(word_to_guess) == len(word_given) and len(letters_in_common) >= 0.65*len(word_to_guess):
                return True, word_to_guess
        return False, None
    
    def word_is_similar(self, word_given, list_words, debug=False):
        word_given = word_given.lower()
        # if debug:
        #     print('Word similar for ',word_given)
        for word_to_guess in [word.lower() for word in list_words]:
            if word_to_guess == word_given:
                return True, word_to_guess
            letters_in_common = set()
            for letter in word_given:
                if letter in word_to_guess:
                    letters_in_common.add(letter)
            # if debug:
            #     print('      ', letters_in_common, word_to_guess)
            if len(word_to_guess) == len(word_given) and len(letters_in_common) >= 0.65*len(word_to_guess):
                return True, word_to_guess
        return False, None
    
    def find_level(self):
        for i, text in enumerate(self.texts):
            if i >= 1:
                if "+" in text.description:
                    break
            if i >= 20:
                raise Exception('ERROR find_level not found')
        coords, center, limit_coords = self.get_coords(text)
        self.localisations["level"] = {
                "found":True,
                "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                 "y":(min(coords)[1],max(coords)[1])},
                "text_raw": text.description,
                "index_found": i,
                "value": text.description[1:],
            }
        print(f'found level: {text.description[1:]}')
        
    def find_type(self):
        for i, text in enumerate(self.texts):
            if i >= self.localisations["level"]['index_found']:
                coords, center, limit_coords = self.get_coords(text)
                if center[1] > self.localisations["level"]['coords_limit']['y'][1]:
                    word_is_similar, similar_word = self.word_is_similar(text.description, self._TYPES)
                    if word_is_similar:
                        break
            if i >= len(self.texts) - 1:
                raise Exception('ERROR find_level not found')
        self.localisations["type"] = {
                "found":True,
                "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                 "y":(min(coords)[1],max(coords)[1])},
                "text_raw": text.description,
                "index_found": i,
                "value": similar_word,
            }
        print(f'found type: {similar_word}')
        
    def find_main_stat(self):
        for i, text in enumerate(self.texts):
            if i >= self.localisations["type"]['index_found']:
                coords, center, limit_coords = self.get_coords(text)
                if center[1] > self.localisations["type"]['coords_limit']['y'][1]:
                    # print('test main stat', text.description, self._STATS)
                    word_is_similar, similar_word = self.word_is_similar(text.description, self._STATS)
                    if word_is_similar:
                        break
            if i >= len(self.texts) - 1:
                raise Exception('ERROR find_level not found')
        self.localisations["main_stat"] = {
                "found":True,
                "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                 "y":(min(coords)[1],max(coords)[1])},
                "text_raw": text.description,
                "index_found": i,
                "value": similar_word,
            }
        print(f'found main_stat: {similar_word}')
        
    def locate_stat_secondaires(self):
        for i, text in enumerate(self.texts):
            if i >= self.localisations["main_stat"]['index_found']:
                coords, center, limit_coords = self.get_coords(text)
                if center[1] > self.localisations["main_stat"]['coords_limit']['y'][1]:
                    # print('test main stat', text.description, self._STATS)
                    if text.description == 'Stats':
                        break
            if i >= len(self.texts) - 1:
                raise Exception('ERROR find_level not found')
        self.localisations["stat_secondaires_location"] = {
                "found":True,
                "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                 "y":(min(coords)[1],max(coords)[1])},
                "index_found": i,
            }
        print(f'found stat secondaire label at index: {i}')
        
    def find_set(self):
        found_set = False
        for i, text in enumerate(self.texts):
            if i >= self.localisations["stat_secondaires_location"]['index_found']:
                coords, center, limit_coords = self.get_coords(text)
                if center[1] > self.localisations["stat_secondaires_location"]['coords_limit']['y'][1]:
                    # print('test main stat', text.description, self._STATS)
                    if text.description == 'Set':
                        found_set = True
                        max_y_set = limit_coords['max_y']
                        min_y_set = limit_coords['min_y']
                    if found_set and center[1]<max_y_set and center[1]>min_y_set:
                        # print('testing similar', text.description, self._SETS)
                        word_is_similar, similar_word = self.word_is_similar(text.description, self._SETS)
                        if word_is_similar:
                            # print('FOUND IT')
                            break
            if i >= len(self.texts) - 1:
                for text in [text for text in self.texts][self.localisations["stat_secondaires_location"]['index_found']:]:
                    print(text.description)
                raise Exception('ERROR set not found')

            
        self.localisations["set"] = {
                "found":True,
                "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                 "y":(min(coords)[1],max(coords)[1])},
                "text_raw": text.description,
                "index_found": i,
                "value": similar_word,
            }
        print(f'found set: {similar_word}')
        


    def find_substats(self):
        
        i_min = self.localisations["stat_secondaires_location"]['index_found']
        coord_stat_sec = self.localisations["stat_secondaires_location"]['coords_limit']

        i_max = self.localisations["set"]['index_found']
        coord_set = self.localisations["set"]['coords_limit']

        def is_str_of_float(v):
            try:
                float(v.replace("%",''))
                return True
            except:
                return False

        substats = {}
        substats_values_coordy = {}
        
        
        list_text = [text for text in self.texts]
        for i, text in enumerate(list_text):
            print(i, text.description)
        print()
        
        list_text = [text for text in self.texts][i_min+2:i_max-1]
        for i, text in enumerate(list_text):
            # print(i, text.description)
            # print()
            # print(text.description, self.get_coords(text)[2])
            coords, center, limit_coords = self.get_coords(text)
            word_is_similar, similar_word = self.word_is_similar(text.description, Decoder._STATS)
            if word_is_similar:
                # print('Found a stat: ', similar_word, limit_coords)
                substats[len(substats)] = {
                    "stat": similar_word,
                    "coords_limit": {"x":(min(coords)[0],max(coords)[0]), 
                                     "y":(min(coords)[1],max(coords)[1])},
                    "text_raw": text.description,
                    "index_found": i,
                    "nbs_procs": ""
                }
                if similar_word in ['taux','dégât'] and list_text[i+3].description[0] == '[':
                    substats[len(substats)-1]["nbs_procs"] = list_text[i+3].description
                    substats[len(substats)-1]["i_proc"] = i+3
                elif list_text[i+1].description[0] == '[':
                    substats[len(substats)-1]["nbs_procs"] = list_text[i+1].description
                    substats[len(substats)-1]["i_proc"] = i+1
            if is_str_of_float(text.description):
                substats_values_coordy[text.description] = center[1]
                print("found a float",text.description)
                # for sub,sub_dic in substats.items():
                #     print('   testing coord',center,sub_dic['coords_limit']['y'],sub_dic['stat'])
                #     if center[1] < sub_dic['coords_limit']['y'][1] and center[1] > sub_dic['coords_limit']['y'][0]:
                #         print("   float",text.description,"is within range of ",sub_dic['stat'])
                #         substats[sub]['value'] = text.description
        if len(substats) == len(substats_values_coordy):
            for index_sub,val in enumerate(sorted(substats_values_coordy.items(), key=lambda item: item[1])):
                # print('added stat',substats[index_sub]['stat'],' +',val[0])
                substats[index_sub]['value'] = val[0]
        else:
            print('ERROR missmatch length between substats and substas_values')
            self.localisations['completed'] = {
                    "is_valid": False,
                    "reason": "missmatch length between substats and substas_values",
                }
                        
        print(f'found {len(substats)} substats')
        self.localisations['substats'] = substats
        
        
    def decode(self, path):
        
        filename = path.split('/')[-1]
        log(f"Decoding image {filename}")
        
        log(f"Exracting full text with OCR {filename}")
        self.texts = OCR().detect_text(path)
        
        self.localisations = {
            "completed": {
                "is_valid": True,
                "reason": "",
            },
            "level":{
                "found":False,
            },
            "type":{
                "found":False,
            },
            "main_stat":{
                "found":False,
            },
            "stat_secondaires_location":{
                "found":False,
            },
            "set":{
                "found":False,
            },
            "substats":{
                "found":False,
            },
        }
        
        
        
        print('starting gear information mining...')
        self.find_level()
        self.find_type()
        self.find_main_stat()
        self.locate_stat_secondaires()
        self.find_set()
        self.find_substats()
        
        
        print(f"Hash: {hash(str(self.localisations))}")
        
        path_target = f"{self.folder_json}/{filename.replace('png','json')}"
        with open(path_target,"w+") as f:
            json.dump(self.localisations, f)
            f.close()
            