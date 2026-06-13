import threading
import json
import websocket
class NetworkClient:
    def __init__(self, url="ws://127.0.0.1:7777", callback=None):
        self.url = url
        self.callback = callback
        self.ws = None
        self.running = False
    def connect(self):
        try:
            websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.running = True
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
            return True
        except Exception as e:
            print(f"критическая ошибка подключения: {e}")
            return False
    def send(self, data):
        if self.ws and self.running:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                print(f"ошибка отправки: {e}")
    def _on_message(self, ws, message):
        try:
            msg = json.loads(message)
            if self.callback:
                self.callback(msg)
        except Exception as e:
            print(f"ошибка парсинга: {e}")
    def _on_error(self, ws, error):
        print(f"ошибка WebSocket: {error}")
    def _on_close(self, ws, close_status_code, close_msg):
        print("Соединение закрыто")
        self.running = False