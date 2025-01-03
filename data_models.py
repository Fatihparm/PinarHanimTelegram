import sqlite3

class Model:
    def __init__(self):
        self.db = sqlite3.connect('database.db', check_same_thread=False)
        self.c = self.db.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS ZodiacSigns(
                id INTEGER PRIMARY KEY,
                name TEXT DEFAULT "", 
                description TEXT DEFAULT "",
                date TEXT,
                image TEXT
            )''')
            
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS TarotCards(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL, 
                description TEXT DEFAULT "",
                image TEXT DEFAULT ""
            )''')
        
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                chat_id TEXT NOT NULL, 
                first_name TEXT DEFAULT "",
                last_name TEXT DEFAULT "",
                message TEXT DEFAULT "",
                message_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                chat_id TEXT PRIMARY KEY NOT NULL, 
                first_name TEXT DEFAULT "",
                last_name TEXT DEFAULT "",
                sign TEXT DEFAULT "",
                subsdate DATETIME DEFAULT CURRENT_TIMESTAMP
            )    
            ''')
        self.db.commit()
    
    def add_message(self, chat_id, first_name, last_name, message):
        """Adds a message to the database"""
        self.c.execute(
        '''
        INSERT INTO messages (chat_id, first_name, last_name, message) 
        VALUES (?, ?, ?, ?)
        ''', (chat_id, first_name, last_name, message))
        self.db.commit()

    def insert_zodiac_sign(self, sign):
        self.c.execute("INSERT INTO ZodiacSigns (name, description, date, image) VALUES (?, ?, ?, ?)", (sign.name, sign.description, sign.date, sign.image))
        self.db.commit()

    def insert_tarot_card(self, card):
        self.c.execute("INSERT INTO TarotCards (name, description, image) VALUES (?, ?, ?)", (card.name, card.description, card.image))
        self.db.commit()

    def add_user(self, chat_id, first_name, last_name, sign):
        """Adds a user to the database"""
        self.c.execute(
        '''
        INSERT OR IGNORE INTO subscriptions (chat_id, first_name, last_name, sign) 
        VALUES (?, ?, ?, ?)
        ''', (chat_id, first_name, last_name, sign))
        self.db.commit()
    
    def delete_person(self, chat_id):
        """Deletes a user from the database"""
        self.c.execute(
        '''
        DELETE FROM subscriptions WHERE chat_id = ?
        ''', (chat_id,))
        self.db.commit()
    
    def check_person(self, chat_id):
        """Checks if a user exists"""
        self.c.execute(
        '''
        SELECT * FROM subscriptions WHERE chat_id = ?
        ''', (chat_id,))
        return self.c.fetchone()

    def check_all(self):
        """Fetches all users"""
        self.c.execute('''
        SELECT * FROM subscriptions 
        ''')
        return self.c.fetchall()

    def get_zodiac_signs(self):
        self.c.execute("SELECT * FROM ZodiacSigns")
        rows = self.c.fetchall()
        signs = [ZodiacSign(row[1], row[2], row[3], row[4]) for row in rows]
        return signs

    def get_tarot_cards(self):
        self.c.execute("SELECT * FROM TarotCards")
        rows = self.c.fetchall()
        cards = [TarotCard(row[1], row[2], row[3]) for row in rows]
        return cards

    def remove_duplicates_if_exists(self):
        self.c.execute("DELETE FROM ZodiacSigns WHERE rowid NOT IN (SELECT MIN(rowid) FROM ZodiacSigns GROUP BY name)")
        self.c.execute("DELETE FROM TarotCards WHERE rowid NOT IN (SELECT MIN(rowid) FROM TarotCards GROUP BY name)")
        self.db.commit()

    def clear_zodiac_signs(self):
        self.c.execute("DELETE FROM ZodiacSigns")
        self.db.commit()
    
    def clear_tarot_cards(self):
        self.c.execute("DELETE FROM TarotCards")
        self.db.commit()

class ZodiacSign():
    def __init__(self, name, description, date, image):
        self.name = name
        self.description = description
        self.date = date
        self.image = image

class TarotCard():
    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image
