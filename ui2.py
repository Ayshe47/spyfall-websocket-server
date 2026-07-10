import os
import sys
import customtkinter as ctk
from PIL import Image
from network import NetworkClient
from tkinter import messagebox


def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

SERVER_URL = os.getenv("SPYFALL_SERVER_URL", "wss://spyfall-websocket-server.onrender.com")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}")
        self.configure(fg_color="white")
        self.title("Spyfall Game")


        try:
            ctk.FontManager.load_font(resource_path("RussoOne.ttf"))
        except:
            pass

        self.network = NetworkClient(url=SERVER_URL, callback=self.network_callback)
        self.is_host = False
        self.room_code = ""
        self.russo_font = ctk.CTkFont(family="Russo One", size=24)
        self.russo_font_btn = ctk.CTkFont(family="Russo One", size=28)
        self.font_pass = ctk.CTkFont(family="Russo One", size=80)
        self.russo_font_big = ctk.CTkFont(family="Russo One", size=40)
        self.russo_font_huge = ctk.CTkFont(family="Russo One", size=50)

        self.is_creating = False
        self.spinner_chars = ["|", "/", "-", "\\"]
        self.spinner_idx = 0

        self.create_menu_screen()
        self.create_join_screen()
        self.create_lobby_screen()
        self.create_role_screen()
        self.create_game_screen()

        self.show_screen(self.menu_frame)

    def create_menu_screen(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color="white")

        try:

            self.menu_bg = ctk.CTkImage(
                light_image=Image.open(resource_path("firstScreen.png")),
                size=(self.screen_width, self.screen_height)
            )
            self.menu_bg_label = ctk.CTkLabel(self.menu_frame, image=self.menu_bg, text="")
            self.menu_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Ошибка загрузки фона меню: {e}")

        self.name_entry = ctk.CTkEntry(
            self.menu_frame, width=650, height=80, corner_radius=0,
            placeholder_text="ВАШЕ ИМЯ", font=self.russo_font_big, justify="center"
        )
        self.name_entry.place(relx=0.55, y=500, anchor="w")

        self.create_btn = ctk.CTkButton(
            self.menu_frame, text="СОЗДАТЬ КОМНАТУ", width=650, height=80,
            corner_radius=0, font=self.russo_font_big, fg_color="black",
            hover_color="#333333", command=self.req_create_room
        )
        self.create_btn.place(relx=0.55, y=650, anchor="w")

        join_screen_btn = ctk.CTkButton(
            self.menu_frame, text="ВОЙТИ В КОМНАТУ", width=650, height=80,
            corner_radius=0, font=self.russo_font_big, fg_color="black",
            hover_color="#333333", command=lambda: self.show_screen(self.join_frame)
        )
        join_screen_btn.place(relx=0.55, y=800, anchor="w")

    def create_join_screen(self):
        self.join_frame = ctk.CTkFrame(self, fg_color="white")

        try:

            join_bg_image = ctk.CTkImage(
                light_image=Image.open(resource_path("joinbk2.png")),
                dark_image=Image.open(resource_path("joinbk2.png")),
                size=(self.screen_width, self.screen_height)
            )
            join_bg_label = ctk.CTkLabel(self.join_frame, image=join_bg_image, text="")
            join_bg_label.place(relwidth=1, relheight=1)
            self.join_bg_image = join_bg_image
        except:
            pass

        self.code_entry = ctk.CTkEntry(
            self.join_frame, width=550, height=80, placeholder_text="Код комнаты", font=self.russo_font_btn,
            justify="center"
        )
        self.code_entry.place(relx=0.5, y=410, anchor="center")

        join_btn = ctk.CTkButton(
            self.join_frame, text="ПОДКЛЮЧИТЬСЯ", width=550, height=80, font=self.russo_font_btn,
            fg_color="#4B555D", hover_color="#363E44", text_color="white", corner_radius=0, command=self.req_join_room
        )
        join_btn.place(relx=0.5, y=520, anchor="center")

        back_btn = ctk.CTkButton(
            self.join_frame, text="НАЗАД", width=550, height=80, font=self.russo_font_btn,
            fg_color="#9EB0BD", hover_color="#82939F", text_color="black", corner_radius=0,
            command=lambda: self.show_screen(self.menu_frame)
        )
        back_btn.place(relx=0.5, y=630, anchor="center")

    def create_lobby_screen(self):
        self.lobby_frame = ctk.CTkFrame(self)

        try:

            bg_image = ctk.CTkImage(
                light_image=Image.open(resource_path("joinbk.png")),
                dark_image=Image.open(resource_path("joinbk.png")),
                size=(self.screen_width, self.screen_height)
            )
            bg_label = ctk.CTkLabel(self.lobby_frame, image=bg_image, text="")
            bg_label.place(relwidth=1, relheight=1)
            self.bg_image = bg_image
        except:
            pass

        self.room_container = ctk.CTkFrame(self.lobby_frame, fg_color="white")
        self.room_container.place(relx=0.5, y=80, anchor="center")

        self.room_prefix_label = ctk.CTkLabel(self.room_container, text="Комната: ", font=self.russo_font_big,
                                              text_color="black")
        self.room_prefix_label.pack(side="left")

        self.room_label = ctk.CTkLabel(self.room_container, text="____", font=self.russo_font_big, text_color="red")
        self.room_label.pack(side="left")

        self.categories = {
            "Математика": 1, "Общение и взаимодействие": 2, "Путешествия": 3,
            "Хобби": 4, "Еда": 5, "Страны": 6
        }

        self.category = ctk.CTkOptionMenu(
            self.lobby_frame, width=550, height=80, values=list(self.categories.keys()),
            fg_color="#D6CFC7", button_color="#C4B9AC", button_hover_color="#B3A89C", text_color="black",
            font=self.russo_font_btn, anchor="center", dropdown_font=self.russo_font
        )
        self.category.set("Выберите тему")
        self.category.place(relx=0.5, y=170, anchor="center")

        ctk.CTkLabel(self.lobby_frame, text="Игроки в лобби:", font=self.russo_font_btn, text_color="black",
                     fg_color="white").place(relx=0.5, y=260, anchor="center")

        self.players_textbox = ctk.CTkTextbox(self.lobby_frame, width=550, height=200, font=self.russo_font,
                                              text_color="black", fg_color="white", border_width=2,
                                              border_color="black")
        self.players_textbox.place(relx=0.5, y=400, anchor="center")
        self.players_textbox.configure(state="disabled")

        self.startbtn = ctk.CTkButton(
            self.lobby_frame, text="НАЧАТЬ ИГРУ", font=self.russo_font_btn, width=550, height=80,
            fg_color="#4B555D", hover_color="#363E44", text_color="white", corner_radius=0, command=self.req_start_game
        )
        self.startbtn.place(relx=0.5, y=560, anchor="center")

        leave_btn = ctk.CTkButton(
            self.lobby_frame, text="ВЫЙТИ ИЗ КОМНАТЫ", font=self.russo_font_btn, width=550, height=80,
            fg_color="#9EB0BD", hover_color="#82939F", text_color="black", corner_radius=0, command=self.req_leave_room
        )
        leave_btn.place(relx=0.5, y=670, anchor="center")

    def create_role_screen(self):
        self.role_frame = ctk.CTkFrame(self)

        try:

            rolebg_image = ctk.CTkImage(
                light_image=Image.open(resource_path("rolebg.png")),
                dark_image=Image.open(resource_path("rolebg.png")),
                size=(self.screen_width, self.screen_height)
            )
            bg_label = ctk.CTkLabel(self.role_frame, image=rolebg_image, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.rolebg_image = rolebg_image
        except:
            pass

        self.role_label = ctk.CTkLabel(self.role_frame, text="", font=self.font_pass, text_color="black",
                                       fg_color="transparent")
        self.role_label.place(relx=0.5, rely=0.21, anchor="center")

        self.ready_button = ctk.CTkButton(
            self.role_frame, text="Понятно, к игре!", width=650, height=90, fg_color="white", hover_color="#E5E5E5",
            font=self.russo_font_huge, text_color="black", corner_radius=0, command=self.req_player_ready
        )
        self.ready_button.place(relx=0.5, y=800, anchor="center")

    def create_game_screen(self):
        self.game_frame = ctk.CTkFrame(self)

        try:
            # Название файла: gamebg.png
            gambck_image = ctk.CTkImage(
                light_image=Image.open(resource_path("gamebg.png")),
                dark_image=Image.open(resource_path("gamebg.png")),
                size=(self.screen_width, self.screen_height)
            )
            bcg_label = ctk.CTkLabel(self.game_frame, image=gambck_image, text="")
            bcg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.gambck_image = gambck_image
        except:
            pass

        self.game_label = ctk.CTkLabel(self.game_frame, text="ИГРА ИДЕТ", fg_color="#D9D9D9", font=self.font_pass,
                                       text_color="black")
        self.game_label.pack(pady=150)

        self.tomenu = ctk.CTkButton(
            self.game_frame, text="Выйти в меню", command=self.req_leave_room, font=self.russo_font_huge,
            width=650, height=100, fg_color="white", hover_color="#E5E5E5", text_color="black", corner_radius=0
        )
        self.tomenu.place(relx=0.5, y=420, anchor="center")

    def ensure_connected(self):
        if not self.network.running:
            return self.network.connect()
        return True

    def animate_loading(self, ticks=0):
        if not self.is_creating:
            self.create_btn.configure(text="СОЗДАТЬ КОМНАТУ", state="normal")
            return

        if ticks > 200:
            self.is_creating = False
            self.create_btn.configure(text="СОЗДАТЬ КОМНАТУ", state="normal")
            messagebox.showerror("Ошибка", "Превышено время ожидания ответа от сервера. Повторите попытку")
            return

        char = self.spinner_chars[self.spinner_idx % len(self.spinner_chars)]
        self.create_btn.configure(text=f"ЗАГРУЗКА {char}", state="disabled")
        self.spinner_idx += 1
        self.after(100, self.animate_loading, ticks + 1)

    def req_create_room(self):
        name = self.name_entry.get().strip() or "Игрок"
        if not self.network.running:
            self.network.connect()
        self.is_creating = True
        self.animate_loading()
        self.after(500, lambda: self.network.send({"type": "create_room", "name": name}))

    def req_join_room(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip() or "Игрок"
        if not code:
            return
        if not self.network.running:
            self.network.connect()
        self.after(500, lambda: self.network.send({"type": "join_room", "code": code, "name": name}))

    def req_start_game(self):
        if not self.is_host:
            return
        cat = self.category.get()
        if cat == "Выберите тему":
            messagebox.showwarning("Внимание", "Пожалуйста, выберите тему перед началом игры.")
            return
        self.network.send({"type": "start_game", "category": self.categories[cat]})

    def req_player_ready(self):
        self.ready_button.configure(state="disabled", text="ОЖИДАНИЕ ИГРОКОВ...")
        if self.network.running:
            self.network.send({"type": "player_ready"})

    def req_leave_room(self):
        if self.network.running:
            self.network.send({"type": "leave_room"})
        self.show_screen(self.menu_frame)

    def network_callback(self, msg):
        self.after(0, self.handle_network_msg, msg)

    def handle_network_msg(self, msg):
        msg_type = msg.get("type")

        if msg_type == "joined_room":
            self.is_creating = False
            self.room_code = msg.get("code")
            self.is_host = msg.get("is_host", False)
            self.room_label.configure(text=self.room_code)
            self.setup_lobby_visibility()
            self.update_players_list(msg.get("players", []))
            self.show_screen(self.lobby_frame)

        elif msg_type == "room_update":
            self.update_players_list(msg.get("players", []))

        elif msg_type == "promoted_to_host":
            self.is_host = True
            self.setup_lobby_visibility()
            messagebox.showinfo("Статус", "Вы стали хостом комнаты!")

        elif msg_type == "game_started":
            self.ready_button.configure(state="normal", text="Понятно, к игре!")
            self.role_label.configure(text=msg.get("role", ""))
            self.show_screen(self.role_frame)

        elif msg_type == "match_start":
            self.show_screen(self.game_frame)

        elif msg_type == "error":
            self.is_creating = False
            messagebox.showerror("Ошибка", msg.get("message", "Произошла ошибка"))

    def setup_lobby_visibility(self):
        if self.is_host:
            self.startbtn.configure(state="normal", text="НАЧАТЬ ИГРУ")
            self.category.configure(state="normal")
        else:
            self.startbtn.configure(state="disabled", text="ОЖИДАНИЕ ХОСТА...")
            self.category.configure(state="disabled")

    def update_players_list(self, players):
        self.players_textbox.configure(state="normal")
        self.players_textbox.delete("1.0", "end")
        for i, p in enumerate(players, 1):
            self.players_textbox.insert("end", f"{i}. {p}\n")
        self.players_textbox.configure(state="disabled")

    def show_screen(self, screen):
        for widget in self.winfo_children():
            if hasattr(widget, 'pack_forget'):
                widget.pack_forget()
        screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()