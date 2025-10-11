class UzbekTranslator:
    """O'zbek tilida Lotin ↔ Kirill konvertatsiya kutubxonasi"""
    
    def __init__(self):
        # Lotin -> Kirill mapping
        self.latin_to_cyrillic = {
            'A': 'А', 'a': 'а',
            'B': 'Б', 'b': 'б',
            'D': 'Д', 'd': 'д',
            'E': 'Е', 'e': 'е',
            'F': 'Ф', 'f': 'ф',
            'G': 'Г', 'g': 'г',
            'H': 'Ҳ', 'h': 'ҳ',
            'I': 'И', 'i': 'и',
            'J': 'Ж', 'j': 'ж',
            'K': 'К', 'k': 'к',
            'L': 'Л', 'l': 'л',
            'M': 'М', 'm': 'м',
            'N': 'Н', 'n': 'н',
            'O': 'О', 'o': 'о',
            'P': 'П', 'p': 'п',
            'Q': 'Қ', 'q': 'қ',
            'R': 'Р', 'r': 'р',
            'S': 'С', 's': 'с',
            'T': 'Т', 't': 'т',
            'U': 'У', 'u': 'у',
            'V': 'В', 'v': 'в',
            'X': 'Х', 'x': 'х',
            'Y': 'Й', 'y': 'й',
            'Z': 'З', 'z': 'з',
            'Oʻ': 'Ў', 'oʻ': 'ў', "O'": 'Ў', "o'": 'ў',
            'Gʻ': 'Ғ', 'gʻ': 'ғ', "G'": 'Ғ', "g'": 'ғ',
            'Sh': 'Ш', 'sh': 'ш', 'SH': 'Ш',
            'Ch': 'Ч', 'ch': 'ч', 'CH': 'Ч',
            'Ye': 'Е', 'ye': 'е', 'YE': 'Е',
            'Yu': 'Ю', 'yu': 'ю', 'YU': 'Ю',
            'Ya': 'Я', 'ya': 'я', 'YA': 'Я',
            'Yo': 'Ё', 'yo': 'ё', 'YO': 'Ё',
            'E': 'Э', 'e': 'э',
        }
        
        # Kirill -> Lotin mapping
        self.cyrillic_to_latin = {
            'А': 'A', 'а': 'a',
            'Б': 'B', 'б': 'b',
            'Д': 'D', 'д': 'd',
            'Е': 'E', 'е': 'e',
            'Ф': 'F', 'ф': 'f',
            'Г': 'G', 'г': 'g',
            'Ҳ': 'H', 'ҳ': 'h',
            'И': 'I', 'и': 'i',
            'Ж': 'J', 'ж': 'j',
            'К': 'K', 'к': 'k',
            'Л': 'L', 'л': 'l',
            'М': 'M', 'м': 'm',
            'Н': 'N', 'н': 'n',
            'О': 'O', 'о': 'o',
            'П': 'P', 'п': 'p',
            'Қ': 'Q', 'қ': 'q',
            'Р': 'R', 'р': 'r',
            'С': 'S', 'с': 's',
            'Т': 'T', 'т': 't',
            'У': 'U', 'у': 'u',
            'В': 'V', 'в': 'v',
            'Х': 'X', 'х': 'x',
            'Й': 'Y', 'й': 'y',
            'З': 'Z', 'з': 'z',
            'Ў': "O'", 'ў': "o'",
            'Ғ': "G'", 'ғ': "g'",
            'Ш': 'Sh', 'ш': 'sh',
            'Ч': 'Ch', 'ч': 'ch',
            'Ю': 'Yu', 'ю': 'yu',
            'Я': 'Ya', 'я': 'ya',
            'Ё': 'Yo', 'ё': 'yo',
            'Э': 'E', 'э': 'e',
        }
    
    def to_cyrillic(self, text):
        """Lotindan Kirillga o'girish"""
        result = text
        
        # Avval 2-3 harfli kombinatsiyalarni almashtirish
        for latin, cyrillic in sorted(self.latin_to_cyrillic.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(latin, cyrillic)
        
        return result
    
    def to_latin(self, text):
        """Kirilldan Lotinga o'girish"""
        result = ""
        
        for char in text:
            result += self.cyrillic_to_latin.get(char, char)
        
        return result
    
    def detect_script(self, text):
        """Matnning qaysi yozuvda ekanligini aniqlash"""
        cyrillic_count = sum(1 for char in text if char in 'АБДЕФГҲИЖКЛМНОПҚРСТУВХЙЗЎҒШЧЮЯЁЭабдефгҳижклмнопқрстувхйзўғшчюяёэ')
        latin_count = sum(1 for char in text if char in 'ABDEFGHIJKLMNOPQRSTUVXYZabdefghijklmnopqrstuvxyz')
        
        if cyrillic_count > latin_count:
            return "cyrillic"
        elif latin_count > cyrillic_count:
            return "latin"
        else:
            return "unknown"
    
    def auto_convert(self, text):
        """Avtomatik aniqlash va konvertatsiya qilish"""
        script = self.detect_script(text)
        
        if script == "cyrillic":
            return self.to_latin(text)
        elif script == "latin":
            return self.to_cyrillic(text)
        else:
            return text


# Kutubxonani ishlatish uchun funksiyalar
def to_cyrillic(text):
    """Lotindan Kirillga"""
    translator = UzbekTranslator()
    return translator.to_cyrillic(text)

def to_latin(text):
    """Kirilldan Lotinga"""
    translator = UzbekTranslator()
    return translator.to_latin(text)

def auto_convert(text):
    """Avtomatik konvertatsiya"""
    translator = UzbekTranslator()
    return translator.auto_convert(text)