import string
from collections import defaultdict
import random
from itertools import product

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
            print(a, b)
            self.keys[a] = b


    def encode(self, a: chr): # Кодировка для дальнейшего использования. Если в словаре есть входная буква, то меняем её на парную ей, если нет - возвращаем без изменений
        for i in self.keys.items():
            if a in i:
                return i[0] if a == i[1] else i[1]
        return a



class Rotor:
    def __init__(self, wiring, notch):
        self.wiring = wiring
        self.notch = notch
        self.position = 0
        self.ring_setting = 0
    
    def encode_forward(self, char):
        shifted_char = chr((ord(char) - ord('A') + self.position - self.ring_setting) % 26 + ord('A'))
        encrypted_char = self.wiring[ord(shifted_char) - ord('A')]
        return chr((ord(encrypted_char) - ord('A') - self.position + self.ring_setting) % 26 + ord('A'))
    
    def encode_backward(self, char):
        shifted_char = chr((ord(char) - ord('A') + self.position - self.ring_setting) % 26 + ord('A'))
        encrypted_pos = self.wiring.index(shifted_char)
        encrypted_char = chr(encrypted_pos + ord('A'))
        return chr((ord(encrypted_char) - ord('A') - self.position + self.ring_setting) % 26 + ord('A'))
    
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
    


Rotor1 = Rotor(ROTOR_I, NOTCHES[0])
Rotor2 = Rotor(ROTOR_II, NOTCHES[1])
Rotor4 = Rotor(ROTOR_IV, NOTCHES[3])
ReflectorB = Reflector(REFLECTOR_B)
Plugboard1 = Plugboard(["AB", "CD", "EF", "GH", "IJ", "KL", "MN", "OP", "QR", "ST"])
Enigma1 = Enigma([Rotor4, Rotor2, Rotor1], ReflectorB, Plugboard1)
EncodedMessage = Enigma1.encode_message("WEATHER")
print(EncodedMessage)

Rotor1 = Rotor(ROTOR_I, NOTCHES[0])
Rotor2 = Rotor(ROTOR_II, NOTCHES[1])
Rotor4 = Rotor(ROTOR_IV, NOTCHES[3])
ReflectorB = Reflector(REFLECTOR_B)
Plugboard2 = Plugboard(["AB", "CD", "EF", "GH", "IJ", "KL", "MN", "OP", "QR", "ST"])
Enigma2 = Enigma([Rotor4, Rotor2, Rotor1], ReflectorB, Plugboard2)
DecodedMessage = Enigma2.encode_message(EncodedMessage)
print(DecodedMessage)


def optimized_crack(ciphertext, known_plaintext, crib_positions):
    """
    Оптимизированный метод с использованием "крибов" (известных фраз)
    crib_positions - возможные позиции известного текста в шифровке
    """
    # Реализация метода "меню" Тьюринга
    # Поиск циклов в сопоставлении известного текста и шифровки
    # Это позволяет исключить множество неподходящих настроек
    
    best_score = 0
    best_config = None
    
    for pos in crib_positions:
        crib = known_plaintext
        cipher_part = ciphertext[pos:pos+len(crib)]
        
        # Упрощенная проверка (в реальности использовались более сложные методы)
        for rotor_comb in [("I", "II", "III"), ("IV", "II", "V"), ("III", "II", "I")]:
            for reflector in ["B", "C"]:
                # Проверка только некоторых позиций
                for pos1, pos2, pos3 in product("ABCDE", repeat=3):
                    enigma = create_enigma(
                        rotor_comb,
                        [pos1, pos2, pos3],
                        [0, 0, 0],
                        [],
                        reflector
                    )
                    
                    decrypted = enigma.encode_message(cipher_part)
                    score = sum(1 for a, b in zip(decrypted, crib) if a == b)
                    
                    if score > best_score:
                        best_score = score
                        best_config = {
                            'rotors': rotor_comb,
                            'positions': [pos1, pos2, pos3],
                            'reflector': reflector
                        }
                        
                        if best_score == len(crib):
                            return best_config
    
    return best_config if best_score > len(known_plaintext) / 2 else None