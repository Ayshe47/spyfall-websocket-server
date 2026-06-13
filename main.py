import random
from datas import maps

class SpyGame:
    def __init__(self, players_count, category_id):
        self.players_count = players_count
        # Серверный индекс шпиона (от 0 до players_count - 1)
        self.spy_index = random.randint(0, players_count - 1)

        try:
            self.location = random.choice(maps[int(category_id)])
        except (KeyError, ValueError):
            # Если передана неверная тема, берем первую доступную
            first_key = list(maps.keys())[0]
            self.location = random.choice(maps[first_key])