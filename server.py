import asyncio
import json
import random
import os
import websockets
from datas import maps
from main import SpyGame
PORT= int(os.environ.get("PORT", 7777))
rooms ={}
class Room:
    def __init__(self, code, host_client, host_name):
        self.code =code
        self.host= host_client
        self.players = [(host_client, host_name)]
        self.category =None
        self.started= False
        self.ready_players= set()
    def get_player_names(self):
        return [name for _,name in self.players]
    async def broadcast(self, data):
        message = json.dumps(data)
        for client, _ in self.players:
            try:
                await client.send(message)
            except:
                pass
def create_room(host_client, host_name):
    while True:
        code = str(random.randint(1000, 9999))
        if code not in rooms:
            rooms[code] = Room(code, host_client, host_name)
            return code
async def handle_client(websocket):
    current_room_code = None
    player_name = "Игрок"
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            if msg_type == "create_room":
                player_name = data.get("name", "Хост")
                code = create_room(websocket, player_name)
                current_room_code = code
                room = rooms[code]

                await websocket.send(json.dumps({
                    "type": "joined_room",
                    "code": code,
                    "is_host": True,
                    "players": room.get_player_names()
                }))
            elif msg_type == "join_room":
                code = data.get("code")
                player_name = data.get("name", "Игрок")

                if code not in rooms:
                    await websocket.send(json.dumps({"type": "error", "message": "Комната не найдена"}))
                    continue
                room = rooms[code]
                if room.started:
                    await websocket.send(json.dumps({"type": "error", "message": "Игра в этой комнате уже идет"}))
                    continue
                room.players.append((websocket, player_name))
                current_room_code = code
                await websocket.send(json.dumps({
                    "type": "joined_room",
                    "code": code,
                    "is_host": False,
                    "players": room.get_player_names()
                }))

                await room.broadcast({"type": "room_update", "players": room.get_player_names()})
            elif msg_type == "start_game":
                if current_room_code not in rooms:
                    continue
                room = rooms[current_room_code]
                if room.host != websocket:
                    continue
                if len(room.players) < 2:
                    await websocket.send(json.dumps({"type": "error", "message": "Нужно минимум 2 игрока!"}))
                    continue
                room.category= data.get("category")
                room.started = True
                room.ready_players.clear()
                game_session = SpyGame(len(room.players), room.category)
                for index, (p_client, _) in enumerate(room.players):
                    role = "ШПИОН" if index == game_session.spy_index else f"Слово: {game_session.location}"
                    try:
                        await p_client.send(json.dumps({
                            "type": "game_started",
                            "role": role
                        }))
                    except:
                        pass
            elif msg_type == "player_ready":
                if current_room_code not in rooms:
                    continue
                room = rooms[current_room_code]
                room.ready_players.add(websocket)

                if len(room.ready_players) == len(room.players):
                    await room.broadcast({"type": "match_start"})

            elif msg_type == "leave_room":
                break
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if current_room_code in rooms:
            room = rooms[current_room_code]
            for item in room.players:
                if item[0] == websocket:
                    room.players.remove(item)
                    break
            if websocket in room.ready_players:
                room.ready_players.remove(websocket)
            if not room.players:
                del rooms[current_room_code]
            else:
                if room.host == websocket:
                    room.host = room.players[0][0]
                    try:
                        await room.host.send(json.dumps({"type": "promoted_to_host"}))
                    except:
                        pass
                if room.started and len(room.ready_players) == len(room.players):
                    await room.broadcast({"type": "match_start"})
                else:
                    await room.broadcast({"type": "room_update", "players": room.get_player_names()})
async def main():
    print(f"Сервер Шпиона запущен на порту {PORT}...")
    async with websockets.serve(handle_client, "0.0.0.0", PORT):
        await asyncio.Future()
if __name__ == "__main__":
    asyncio.run(main())