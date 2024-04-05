import tkinter as tk
from tkinter import ttk
import hashlib
import base64
import secrets
import sqlite3
import os
import re

class CreditCardTokenizer:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_token(self, name, card_number, exp_date, cvv):
        # Kredi kartı bilgilerini birleştir
        card_info = f"{card_number}{exp_date}{cvv}"

        # Güvenli rastgele bir token oluştur
        token = secrets.token_hex(16)

        # Token'ı şifrele
        encrypted_token = self._encrypt_token(token)

        # Sadece isim ve token'i döndür
        return {
            "name": name,
            "token": encrypted_token
        }

    def _encrypt_token(self, token):
        # Token'ı şifreleme işlemi 
        hashed_token = hashlib.sha256(f"{token}{self.secret_key}".encode()).hexdigest()

        # Şifrelenmiş token'ı Base64 formatına çevir
        encrypted_token = base64.b64encode(hashed_token.encode()).decode()

        return encrypted_token

class CreditCardDatabase:
    def __init__(self, db_file="credit_cards.db"):
        self.db_file = db_file
        self.connection = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                token TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def insert_credit_card(self, name, token):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO credit_cards (name, token)
            VALUES (?, ?)
        ''', (name, token))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

class CreditCardTokenizationApp:
    def __init__(self, root, tokenizer, database):
        self.root = root
        self.root.title("Kredi Kartı Tokenizasyon Uygulaması")
        self.tokenizer = tokenizer
        self.database = database

        self.create_widgets()

    def create_widgets(self):
        # İsim Soyisim giriş alanı
        ttk.Label(self.root, text="İsim Soyisim:").grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.root)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Kart Numarası giriş alanı
        ttk.Label(self.root, text="Kart Numarası:").grid(row=1, column=0, padx=10, pady=10)
        self.card_number_entry = ttk.Entry(self.root)
        self.card_number_entry.grid(row=1, column=1, padx=10, pady=10)
        # Giriş kontrolü ekleyerek 16 karakter sınırlamasını uygula
        self.card_number_entry.config(validate="key", validatecommand=(self.root.register(self.validate_card_number), "%P"))

        # Son Kullanma Tarihi giriş alanı
        ttk.Label(self.root, text="Son Kullanma Tarihi (MM/YY):").grid(row=2, column=0, padx=10, pady=10)
        self.exp_date_entry = ttk.Entry(self.root)
        self.exp_date_entry.grid(row=2, column=1, padx=10, pady=10)
        # Giriş kontrolü ekleyerek MM/YY formatını zorla
        self.exp_date_entry.config(validate="key", validatecommand=(self.root.register(self.validate_exp_date), "%P"))

        # CVV giriş alanı
        ttk.Label(self.root, text="CVV:").grid(row=3, column=0, padx=10, pady=10)
        self.cvv_entry = ttk.Entry(self.root)
        self.cvv_entry.grid(row=3, column=1, padx=10, pady=10)
        # Giriş kontrolü ekleyerek 3 karakter sınırlamasını uygula
        self.cvv_entry.config(validate="key", validatecommand=(self.root.register(self.validate_cvv), "%P"))

        # Token oluşturma butonu
        ttk.Button(self.root, text="Token Oluştur", command=self.generate_token).grid(row=4, column=0, columnspan=2, pady=10)

    def generate_token(self):
        name = self.name_entry.get()
        card_number = self.card_number_entry.get()
        exp_date = self.exp_date_entry.get()
        cvv = self.cvv_entry.get()

        # Token oluşturucuyu kullanarak token oluştur
        tokenized_card = self.tokenizer.generate_token(name, card_number, exp_date, cvv)

        # Veritabanına sadece isim ve token eklenir
        self.database.insert_credit_card(
            name=name,
            token=tokenized_card["token"]
        )

        result_text = f"İsim Soyisim: {name}\nToken: {tokenized_card['token']}"
        ttk.Label(self.root, text=result_text).grid(row=5, column=0, columnspan=2, pady=10)

    def validate_card_number(self, input_text):
        # Girişin sadece sayılardan oluştuğunu ve uzunluğunun 16 olduğunu kontrol et
        return bool(re.match("^[0-9]*$", input_text)) and len(input_text) <= 16

    def validate_exp_date(self, input_text):
        # Girişin sadece sayılardan oluştuğunu ve MM/YY formatına uygun olduğunu kontrol et
        return bool(re.match("^[0-9/]*$", input_text)) and len(input_text) <= 5

    def validate_cvv(self, input_text):
        # Girişin sadece sayılardan oluştuğunu ve uzunluğunun 3 olduğunu kontrol et
        return bool(re.match("^[0-9]*$", input_text)) and len(input_text) <= 3

# Yeni bir veritabanı dosyası oluştur
new_db_file = "new_credit_cards.db"
if os.path.exists(new_db_file):
    os.remove(new_db_file)

# Tkinter uygulamasını başlat
root = tk.Tk()

# CreditCardTokenizer ve CreditCardDatabase örneklerini oluştur
tokenizer = CreditCardTokenizer(secret_key="gizli_anahtar")
database = CreditCardDatabase(db_file=new_db_file)

# Uygulama penceresini oluştur ve başlat
app = CreditCardTokenizationApp

app = CreditCardTokenizationApp(root, tokenizer, database)
root.mainloop()

# Uygulama kapanırken veritabanı bağlantısını kapat
database.close_connection()