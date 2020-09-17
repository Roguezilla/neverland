import base64
import random
import hashlib

def outer_salt(thing):
    state = random.getstate()
    seed = base64.b64encode(bytes(thing[::-1], encoding='utf8'))
    random.seed(seed)
    outer_salt = ''.join(random.sample(thing, len(thing))) + ''.join(random.sample(seed.decode('utf-8'), len(seed.decode('utf-8'))))
    random.setstate(state)
    return outer_salt

def inner_salt(thing):
    state = random.getstate()
    seed = base64.b64encode(bytes(thing, encoding='utf8'))
    random.seed(seed)
    inner_salt = ''.join(random.sample(thing, len(thing))) + outer_salt(thing) + ''.join(random.sample(seed.decode('utf-8'), len(seed.decode('utf-8'))))
    random.setstate(state)
    return inner_salt

def hash_my_ass(thing):
    return hashlib.sha256(bytes(outer_salt(thing) + hashlib.sha256(bytes(inner_salt(thing) + thing + inner_salt(thing), encoding='utf8')).hexdigest(), encoding='utf8')).hexdigest()

print(hash_my_ass('senha123qweA'))