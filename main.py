import random
from datas import maps
class SpyGame:
    def __init__(self, players_count, category_id):
        self.players_count = players_count
        self.spy_index = random.randint(0, players_count - 1)
        try:
            self.location =random.choice(maps[int(category_id)])
        except (KeyError, ValueError):
            first_key =list(maps.keys())[0]
            self.location= random.choice(maps[first_key])