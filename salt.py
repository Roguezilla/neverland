import base64
import random
import hashlib

def salt(password):
    state = random.getstate()
    seed = base64.b64encode(bytes(password, encoding='utf8'))
    random.seed(seed)
    fuckedup = password + ''.join(random.sample(password, len(password))) + ''.join(random.sample(seed.decode('utf-8'), len(seed.decode('utf-8'))))
    random.setstate(state)
    return fuckedup

def salt_hash(password):
    salted = salt(password)
    return hashlib.sha256(bytes(salted, encoding='utf8')).hexdigest()