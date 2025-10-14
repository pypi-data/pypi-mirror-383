import os
import time

def lazyid(id_str=None):
    
    TIME_LENGTH = 8
    TOTAL_LENGTH = 16
    BASE = 36
    TIME_MODULO = BASE ** TIME_LENGTH
    RANDOM_BYTES_NEEDED = 6
    
    def base36_encode(number):
        if number == 0:
            return '0'
        
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''
        
        while number:
            number, remainder = divmod(number, BASE)
            result = alphabet[remainder] + result
        
        return result

    if id_str:
        time_part = id_str[:TIME_LENGTH]
        return int(time_part, BASE)

    current_time_ms = int(time.time() * 1000)
    time_component = current_time_ms % TIME_MODULO

    random_bytes = os.urandom(RANDOM_BYTES_NEEDED)
    random_component = int.from_bytes(random_bytes, 'big') % TIME_MODULO

    combined = (time_component * TIME_MODULO) + random_component
    
    result = base36_encode(combined)
    return result.zfill(TOTAL_LENGTH)
