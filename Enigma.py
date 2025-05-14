import string
from collections import defaultdict
import random
from itertools import product
import time
# Роторы(исторически точные параметры)
ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
ROTOR_IV = "ESOVPZJAYQUIRHXLNFTGKDCMWB"
ROTOR_V = "VZBRGITYUPSDNHLXAWMJQOFECK"

# Рефлекторы(исторически точные параметры)
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
REFLECTOR_C = "FVPJIAOYEDRZXWGCTKUQSBNMHL"


NOTCHES = [16, 4, 21, 9, 25]


class Plugboard: # Класс входной панели
    def __init__(self, keys: list): # Получаем на вход словарь и устанавливаем соответствие между символами 
        self.keys = dict()
        for pair in keys:
            a, b = pair.upper()[0], pair.upper()[1]
            self.keys[a] = b


    def encode(self, a: chr): # Кодировка для дальнейшего использования. Если в словаре есть входная буква, то меняем её на парную ей, если нет - возвращаем без изменений
        for i in self.keys.items():
            if a in i:
                return i[0] if a == i[1] else i[1]
        return a



class Rotor:
    def __init__(self, wiring, notch, position):
        self.wiring = wiring
        self.notch = notch
        self.position = position
    
    def encode_forward(self, char):
        shifted_char = chr((ord(char) - ord('A') + self.position) % 26 + ord('A'))
        encrypted_char = self.wiring[ord(shifted_char) - ord('A')]
        return chr((ord(encrypted_char) - ord('A') - self.position) % 26 + ord('A'))
    
    def encode_backward(self, char):
        shifted_char = chr((ord(char) - ord('A') + self.position) % 26 + ord('A'))
        encrypted_pos = self.wiring.index(shifted_char)
        encrypted_char = chr(encrypted_pos + ord('A'))
        return chr((ord(encrypted_char) - ord('A') - self.position) % 26 + ord('A'))
    
    def rotate(self):
        self.position = (self.position + 1) % 26
        return self.position == self.notch

class Reflector:
    def __init__(self, wiring):
        self.wiring = wiring
    
    def reflect(self, char):
        return self.wiring[ord(char) - ord('A')]


class Enigma:
    def __init__(self, rotors, reflector, plugboard):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard
    
    def encode_char(self, char):
        # Преобразование через панель коммутации
        char = self.plugboard.encode(char)
        
        # Вращение роторов
        rotate_next = True
        for rotor in self.rotors:
            if rotate_next:
                rotate_next = rotor.rotate()
            else:
                break
        
        # Проход через роторы вперед
        for rotor in self.rotors:
            char = rotor.encode_forward(char)
        
        # Отражение
        char = self.reflector.reflect(char)
        
        # Проход через роторы назад
        for rotor in reversed(self.rotors):
            char = rotor.encode_backward(char)
        
        # Обратное преобразование через панель коммутации
        char = self.plugboard.encode(char)
        
        return char
    
    def encode_message(self, message):
        encoded = []
        for char in message.upper():
            if char in string.ascii_uppercase:
                encoded.append(self.encode_char(char))
        return ''.join(encoded)
    

def crack_enigma(ciphertext, known_plaintext, positions):

    best_score = 0
    best_config = None
    
    for pos in positions:
        crib = known_plaintext
        cipher_part = ciphertext[pos:pos+len(crib)]
        
        for rotor_comb in [(ROTOR_II, ROTOR_IV, ROTOR_V), (ROTOR_III, ROTOR_I, ROTOR_IV)]:
            notches = []
            for i in rotor_comb:
                if i == ROTOR_I:
                    notches.append(NOTCHES[0])
                elif i == ROTOR_II:
                    notches.append(NOTCHES[1])
                elif i == ROTOR_III:
                    notches.append(NOTCHES[2])
                elif i == ROTOR_IV:
                    notches.append(NOTCHES[3])
                else:
                    notches.append(NOTCHES[4])
            for reflect in [REFLECTOR_B, REFLECTOR_C]:

                for pos1, pos2, pos3 in product("ABCDEFGHIJKLMNOPQRSTUVWXYZ", repeat=3):
                    Rotor1, Rotor2, Rotor3 = Rotor(rotor_comb[0], notches[0], ord(pos1) - ord("A")), Rotor(rotor_comb[1], notches[1], ord(pos2) - ord("A")), Rotor(rotor_comb[2], notches[2], ord(pos3) - ord("A"))
                    Reflect = Reflector(reflect)
                    PlugboardE = Plugboard([])
                    enigma = Enigma(
                        [Rotor1, Rotor2, Rotor3], 
                        Reflect, 
                        PlugboardE
                    )
                    
                    decrypted = enigma.encode_message(cipher_part)
                    score = sum(1 for a, b in zip(decrypted, crib) if a == b)
                    if score > best_score:
                        best_score = score
                        best_config = {
                            'rotors': [Rotor1.wiring, Rotor2.wiring, Rotor3.wiring],
                            'positions': [pos1, pos2, pos3],
                            'reflector': Reflect.wiring
                        }
                        
                        if best_score == len(crib):
                            return best_config
    
    return best_config if best_score > (len(known_plaintext) / 2) else None
    


Rotor1 = Rotor(ROTOR_III, NOTCHES[2], 25)
Rotor2 = Rotor(ROTOR_I, NOTCHES[0], 25)
Rotor3 = Rotor(ROTOR_IV, NOTCHES[3], 25)
ReflectorC = Reflector(REFLECTOR_B)
Plugboard1 = Plugboard([])
Enigma1 = Enigma([Rotor1, Rotor2, Rotor3], ReflectorC, Plugboard1)
EncodedMessage = Enigma1.encode_message("ATTACKPOINTB")

print(EncodedMessage)

start = time.time()
print(crack_enigma(EncodedMessage, "ATTACK", [0, 1, 2, 3, 4, 5, 6]))
end = time.time()
print(end - start)
