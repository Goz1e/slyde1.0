import uuid
import string
import random

def random_uuid():
    id = str(uuid.uuid4())[:4].lower()
    y = random.choice(list(string.ascii_lowercase))
    x = id[random.choice(range(0,4))]
    id = id.replace(x,y)
    return id

print(random_uuid())