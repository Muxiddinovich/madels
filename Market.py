import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

PRODUCTS_FILE = "products.json"
USERS_FILE = "users.json"
TELEGRAM_BOT_TOKEN = "7731121943:AAHzqTmZxZhrjAv6iI27SuRQTtXCK9NIxq4"
CHAT_ID = "7888620964"

def load_data(filename, default_value):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

class RegisterScreen(BoxLayout):
    def __init__(self, switch_screen, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.switch_screen = switch_screen

        self.add_widget(Label(text="📝 Ro'yxatdan o'tish", font_size=24, bold=True))

        self.username = TextInput(hint_text="Foydalanuvchi nomi", font_size=18, size_hint=(1, 0.2))
        self.password = TextInput(hint_text="Parol", password=True, font_size=18, size_hint=(1, 0.2))

        self.register_btn = Button(text="✅ Ro‘yxatdan o‘tish", font_size=20, size_hint=(1, 0.3), background_color=(0, 0.6, 0, 1))
        self.register_btn.bind(on_press=self.register)

        self.add_widget(self.username)
        self.add_widget(self.password)
        self.add_widget(self.register_btn)

    def register(self, instance):
        users = load_data(USERS_FILE, {"admin": "admin123"})
        username = self.username.text.strip()
        password = self.password.text.strip()

        if not username or not password:
            self.add_widget(Label(text="⚠️ Iltimos, foydalanuvchi nomi va parol kiriting!", color=(1, 0, 0, 1)))
            return

        if username in users:
            self.add_widget(Label(text="⚠️ Bu username allaqachon mavjud!", color=(1, 0, 0, 1)))
        else:
            users[username] = password
            save_data(USERS_FILE, users)
            self.switch_screen("login")

class ProductSelectionScreen(BoxLayout):
    def __init__(self, switch_screen, store_app, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.switch_screen = switch_screen
        self.store_app = store_app
        self.selected_product = None
        self.add_widget(Label(
            text=f"🛒 Mahsulotlarni tanlang ",
            color=("white"),
            font_size=25,
            size_hint_y=None,
            height=30,
            bold=True
        ))

        self.product_list = GridLayout(cols=2, size_hint_y=None)
        self.product_list.bind(minimum_height=self.product_list.setter('height'))

        self.load_products()

        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_view.add_widget(self.product_list)
        self.add_widget(scroll_view)

        self.order_btn = Button(text="🛒 Zakaz berish", size_hint=(1, 0.1))
        self.order_btn.bind(on_press=self.order_products)
        self.add_widget(self.order_btn)

        self.exit_btn = Button(text="🚪 Chiqish", size_hint=(1, 0.1), on_press=lambda x: self.switch_screen("login"))
        self.add_widget(self.exit_btn)

    def load_products(self):
        products = load_data(PRODUCTS_FILE, [])
        for product in products:
            product_button = Button(
                text=f"{product['name']} - {product['price']} so'm",
                size_hint_y=None,
                height=50,
                background_color=(0.8, 0.8, 0.8, 0.7)
            )
            product_button.bind(on_press=lambda instance, name=product['name']: self.select_product(name))
            self.product_list.add_widget(product_button)

    def select_product(self, product_name):
        self.selected_product = product_name
        self.add_widget(Label(
            text=f"📦 Tanlangan mahsulot: {self.selected_product}",
            color=(0, 0, 1, 1),
            font_size=16,
            size_hint_y=None,
            height=30
        ))

    def order_products(self, instance):
        if self.selected_product:
            user = self.store_app.current_user
            order_message = f"🛒 {user} {self.selected_product} mahsulotini zakaz qildi."
            send_telegram_message(order_message)
            success_label = Label(text="✅ Zakaz muvaffaqiyatli yuborildi!", color=(0, 1, 0, 1),
                                  font_size=16, size_hint_y=None, height=30)
            self.add_widget(success_label)
        else:
            error_label = Label(text="⚠️ Iltimos, mahsulot tanlang!", color=(1, 0, 0, 1),
                                font_size=16, size_hint_y=None, height=30)
            self.add_widget(error_label)

class AdminScreen(BoxLayout):
    def __init__(self, switch_screen, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.switch_screen = switch_screen

        self.add_widget(Label(
            text=f"🛒 Mahsulotlarni boshqarish ",
            color=("white"),
            font_size=25,
            size_hint_y=None,
            height=30,
            bold=True
        ))

        self.name = TextInput(hint_text="Mahsulot nomi", font_size=20, size_hint=(1, 0.2))
        self.price = TextInput(hint_text="Narxi", font_size=20, size_hint=(1, 0.2))
        self.quantity = TextInput(hint_text="Miqdori", font_size=20, size_hint=(1, 0.2))

        self.add_btn = Button(text="➕ Qo‘shish", font_size=20, size_hint=(1, 0.3), background_color=(0, 0.6, 0, 1))
        self.add_btn.bind(on_press=self.add_product)

        self.delete_btn = Button(text="🗑 O‘chirish", font_size=20, size_hint=(1, 0.3), background_color=(1, 0, 0, 1))
        self.delete_btn.bind(on_press=self.remove_product)

        self.message_label = Label(text="", font_size=25,
            size_hint_y=None,
            height=30,
            color=(0, 1, 0, 1))
        self.message_labelr = Label(text="", font_size=25,
            size_hint_y=None,
            height=30,
            color=(1, 0, 0, 1))

        self.exit_btn = Button(text="🚪 Chiqish", font_size=18, size_hint=(1, 0.3), background_color=(0.6, 0, 0, 1))
        self.exit_btn.bind(on_press=lambda x: self.switch_screen("login"))

        self.add_widget(self.name)
        self.add_widget(self.price)
        self.add_widget(self.quantity)
        self.add_widget(self.add_btn)
        self.add_widget(self.delete_btn)
        self.add_widget(self.message_label)
        self.add_widget(self.message_labelr)
        self.add_widget(self.exit_btn)

    def add_product(self, instance):
        name = self.name.text.strip()
        price = self.price.text.strip()
        quantity = self.quantity.text.strip()

        if not name or not price or not quantity:
            self.message_labelr.text = "⚠️ Barcha maydonlarni to‘ldiring!"
            return

        products = load_data(PRODUCTS_FILE, [])
        for product in products:
            if product["name"].lower() == name.lower():
                self.message_labelr.text = f"⚠️ {name} allaqachon qo‘shilgan!"
                return

        new_product = {
            "name": name,
            "price": price,
            "quantity": quantity
        }

        products.append(new_product)
        save_data(PRODUCTS_FILE, products)
        self.message_label.text = f"✅ {name} muvaffaqiyatli qo‘shildi!"

    def remove_product(self, instance):
        name = self.name.text.strip()

        if not name:
            self.message_labelr.text = "⚠️ Iltimos, mahsulot nomini kiriting!"
            return

        products = load_data(PRODUCTS_FILE, [])
        updated_products = [product for product in products if product["name"].lower() != name.lower()]

        if len(products) == len(updated_products):
            self.message_labelr.text = f"⚠️ {name} topilmadi!"
            return

        save_data(PRODUCTS_FILE, updated_products)
        self.message_label.text = f"✅ {name} muvaffaqiyatli o‘chirildi!"

class LoginScreen(BoxLayout):
    def __init__(self, switch_screen, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.switch_screen = switch_screen

        self.add_widget(Label(text="🔑 Kirish", font_size=24, bold=True))

        self.username_input = TextInput(hint_text="Foydalanuvchi nomi", font_size=18, size_hint=(1, 0.2))
        self.password_input = TextInput(hint_text="Parol", password=True, font_size=18, size_hint=(1, 0.2))

        self.login_btn = Button(text="🔓 Kirish", font_size=20, size_hint=(1, 0.3), background_color=(0, 0.5, 1, 1))
        self.login_btn.bind(on_press=self.login)

        self.register_btn = Button(text="📝 Ro‘yxatdan o‘tish", font_size=18, size_hint=(1, 0.2), background_color=(0.8, 0.8, 0.8, 1))
        self.register_btn.bind(on_press=lambda x: self.switch_screen("register"))

        self.error_label = Label(text="", font_size=18, color=(1, 0, 0, 1))

        self.add_widget(self.username_input)
        self.add_widget(self.password_input)
        self.add_widget(self.login_btn)
        self.add_widget(self.register_btn)
        self.add_widget(self.error_label)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        users = load_data(USERS_FILE, {"admin": "admin123"})

        if username in users and users[username] == password:
            self.switch_screen("admin" if username == "admin" else "product_selection")
        else:
            self.show_temp_message("⚠️ Login failed!", 0.7)

    def show_temp_message(self, message, duration):
        self.error_label.text = message
        Clock.schedule_once(lambda dt: self.clear_message(), duration)

    def clear_message(self):
        self.error_label.text = ""

class StoreApp(App):
    def build(self):
        self.current_user = None
        self.screen_manager = BoxLayout()
        self.switch_screen("login")
        return self.screen_manager

    def switch_screen(self, screen_name):
        self.screen_manager.clear_widgets()
        if screen_name == "login":
            self.screen_manager.add_widget(LoginScreen(self.switch_screen))
        elif screen_name == "register":
            self.screen_manager.add_widget(RegisterScreen(self.switch_screen))
        elif screen_name == "product_selection":
            self.screen_manager.add_widget(ProductSelectionScreen(self.switch_screen, self))
        elif screen_name == "admin":
            self.screen_manager.add_widget(AdminScreen(self.switch_screen))

if __name__ == "__main__":
    StoreApp().run()