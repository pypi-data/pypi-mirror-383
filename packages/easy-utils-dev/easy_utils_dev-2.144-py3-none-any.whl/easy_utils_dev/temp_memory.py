


from easy_utils_dev.utils import generateToken , getTimestamp   , start_thread
from time import sleep
import gc

class TemporaryMemory :
    def __init__(self) :
        self.store = {}
        self.deletions=[]
        self.set = self.save
        start_thread(target=self.checker , daemon=False)

    def checker(self) :
        while True :
            sleep(5)
            now = getTimestamp()
            for key, value in list(self.store.items()) :
                if value.get('removeTimestamp') :
                    if now >= value.get('removeTimestamp' , 0) :
                        if value.get('store_deleted_key' , False) :
                            self.deletions.append(key)
                        self.delete(key)

    def delete(self , key ) :
        try :
            del self.store[key]
        except :
            pass
        gc.collect()

    def get(self , key , default=None ) :
        return self.store.get(key , {}).get('item' , default)

    def save(self, item , custom_key=None ,auto_destroy_period=60 , store_deleted_key=True) :
        now = getTimestamp()
        if auto_destroy_period :
            later = getTimestamp(after_seconds=auto_destroy_period)
        else :
            later = None
        if not custom_key :
            custom_key = f"{getTimestamp()}-{generateToken(iter=4)}".upper()
        self.store[custom_key] = {
            'removeTimestamp' : later ,
            'createTimestamp' : now ,
            'item' : item,
            'key' : custom_key ,
            'store_deleted_key' : store_deleted_key
        }
        return custom_key

