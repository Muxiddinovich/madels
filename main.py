import sqlite3
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
# from kivy.uix.listview import ListView, ListAdapter
# from kivy.uix.listview import ListItemButton




class Product:
    """Mahsulot klassi"""
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Cart:
    """Savatcha klassi"""
    def __init__(self):
        self._cart = []  # Inkapsulyatsiya

    def add_product(self, product):
        self._cart.append(product)

    def remove_product(self, product_name):
        self._cart = [p for p in self._cart if p.name != product_name]

    def total_price(self):
        return sum(p.price for p in self._cart)

    def show_cart(self):
        return [str(p) for p in self._cart]


class User:
    """Foydalanuvchi klassi"""
    def __init__(self, name):
        self.name = name
        self.cart = Cart()

    def __str__(self):
        return f"Foydalanuvchi: {self.name}"


class Order(Cart):
    """Buyurtma klassi (Cart'dan voris olgan)"""
    def __init__(self, user):
        super().__init__()  # Cart funksiyalarini oladi
        self.user = user
        self._cart = user.cart._cart[:]  # Cart’ni nusxalash
        self.total = user.cart.total_price()

    def complete_order(self):
        self.user.cart._cart = []  # Savatchani tozalash
        return f"Buyurtma bajarildi! Umumiy narx: ${self.total}"


class Store:
    """Do‘kon klassi"""
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def show_products(self):
        return [str(p) for p in self.products]


class System:
    """Tizim klassi (barcha ma’lumotlarni saqlaydi)"""
    def __init__(self):
        self.store = Store()
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def show_users(self):
        return [str(u) for u in self.users]





class CartApp(App):
    def build(self):
        self.system = System()
        
        # Mahsulotlarni qo‘shish
        self.system.store.add_product(Product("Olma", 2))
        self.system.store.add_product(Product("Banan", 1.5))
        self.system.store.add_product(Product("Shaftoli", 3))

        self.user = User("Ali")
        self.system.add_user(self.user)

        layout = BoxLayout(orientation='vertical')

        self.label = Label(text="Do‘kondagi mahsulotlar:")
        layout.add_widget(self.label)

        # Mahsulot tugmalari
        for product in self.system.store.products:
            btn = Button(text=f"{product.name} - ${product.price}")
            btn.bind(on_press=lambda instance, p=product: self.add_to_cart(p))
            layout.add_widget(btn)

        # Savatcha va umumiy narx
        self.cart_label = Label(text="Savatcha: Bo‘sh")
        layout.add_widget(self.cart_label)

        self.clear_button = Button(text="Savatchani tozalash")
        self.clear_button.bind(on_press=self.clear_cart)
        layout.add_widget(self.clear_button)

        return layout

    def add_to_cart(self, product):
        self.user.cart.add_product(product)
        self.update_cart_label()

    def clear_cart(self, instance):
        self.user.cart._cart = []
        self.update_cart_label()

    def update_cart_label(self):
        if self.user.cart._cart:
            text = "Savatcha:\n" + "\n".join([p.name for p in self.user.cart._cart])
        else:
            text = "Savatcha: Bo‘sh"
        self.cart_label.text = text

def create_users_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# ===== LOGIN SCREEN =====
class LoginScreen(BoxLayout):
    def __init__(self, switch_to_main, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.switch_to_main = switch_to_main
        self.label = Label(text="Login")
        self.username = TextInput(hint_text="Username")
        self.password = TextInput(hint_text="Password", password=True)
        self.login_button = Button(text="Login")
        self.register_button = Button(text="Register")
        
        self.login_button.bind(on_press=self.login)
        self.register_button.bind(on_press=self.register)
        
        self.add_widget(self.label)
        self.add_widget(self.username)
        self.add_widget(self.password)
        self.add_widget(self.login_button)
        self.add_widget(self.register_button)

    def login(self, instance):
        if check_user(self.username.text, self.password.text):
            self.switch_to_main(self.username.text)
        else:
            self.label.text = "Login failed! Try again."

    def register(self, instance):
        if register_user(self.username.text, self.password.text):
            self.label.text = "Registered successfully! Now login."
        else:
            self.label.text = "Username already exists!"

# ===== MAIN APP =====
class CartApp(App):
    def build(self):
        create_users_table()
        self.root = LoginScreen(self.switch_to_main)
        return self.root

    def switch_to_main(self, username):
        self.root.clear_widgets()
        self.root.add_widget(Label(text=f"Welcome, {username}!"))
        self.root.add_widget(Button(text="Logout", on_press=self.restart_app))

    def restart_app(self, instance):
        self.root.clear_widgets()
        self.root.__init__(self.switch_to_main)  # Reset login screen

if __name__ == "__main__":
    CartApp().run()
