import base64
import random
from cryptography.hazmat.primitives import hashes

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

def salt(thing):
    state = random.getstate()
    seed = base64.b64encode(bytes(thing, encoding='utf8'))
    random.seed(seed)
    fuckedup = thing + ''.join(random.sample(thing, len(thing))) + ''.join(random.sample(seed.decode('utf-8'), len(seed.decode('utf-8'))))
    random.setstate(state)
    return fuckedup

def hash_my_ass(thing):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(bytes(inner_salt(thing) + thing + inner_salt(thing), encoding='utf-8'))
    hash1 = str(digest.finalize())

    digest = hashes.Hash(hashes.SHA256())
    digest.update(bytes(salt(outer_salt(thing) + hash1), encoding='utf-8'))
    return str(digest.finalize())