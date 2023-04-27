import os
import random
import time

from core.models import Event, Gift


def match_and_create_gift_for_attenders(event: Event):
    seed = int(time.time()) + int.from_bytes(os.urandom(4))
    random.seed(seed)
    attenders = list(event.attenders.all())
    random.shuffle(attenders)

    for i in range(len(attenders)):
        if i == len(attenders) - 1:
            giver = attenders[i]
            reciver = attenders[0]
        else:
            giver = attenders[i]
            reciver = attenders[i+1]
        Gift.objects.create(giver=giver, reciver=reciver, event=event)

    return True
