import json
import random
from importlib import resources 

DATA_FILE = 'a313_data.json'

def _load_a313_list():
    try:
        data = resources.files('a313').joinpath(DATA_FILE).read_text(encoding='utf-8')
        return json.loads(data)
    except Exception as e:
        raise FileNotFoundError(f"فشل في تحميل قائمة الأذكار من الملف الداخلي: {e}")

def get_random_tofey():
    a313_list = _load_a313_list()
    
    if not a313_list:
        return "لا توجد أذكار متاحة حالياً."
        
    random_tofey = random.choice(a313_list)

    return random_tofey
