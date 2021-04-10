from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from random import shuffle
from cryptography.fernet import Fernet
from Secrets import *
import string
import random
import bcrypt
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    __tablename__ = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password_bank_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_name, password_bank_id):
        self.user_name = user_name
        self.password_bank_id = password_bank_id

class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "user_name")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class PasswordBank(db.Model):
    __tablename__ = "PasswordBank"
    password_bank_id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, password_hash):
        self.password_hash = password_hash

class PasswordBankSchema(ma.Schema):
    class Meta:
        fields = ("password_bank_id", "password_hash")

password_bank_schema = PasswordBankSchema()
password_banks_chema = PasswordBankSchema(many=True)

class Website(db.Model):
    __tablename__ = "Website"
    website_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    website_name = db.Column(db.LargeBinary, nullable=False)
    website_username = db.Column(db.LargeBinary, nullable=False)
    website_password = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, user_id, website_name, website_username, website_password):
        self.user_id = user_id
        self.website_name = website_name
        self.website_username = website_username
        self.website_password = website_password


class WebsiteSchema(ma.Schema):
    class Meta:
        fields = ("website_id", "user_id", "website_name", "website_username", "website_password")

website_schema = WebsiteSchema()
websites_schema = WebsiteSchema(many=True)

def shuffle_word(word):
    word = list(word)
    shuffle(word)
    return ''.join(word)

def create_password():
    letters = string.ascii_lowercase
    numbers = string.digits
    uppercase = string.ascii_uppercase
    numbersAndLetters = ''.join(random.choice(letters) for i in range(10)) + ''.join(random.choice(numbers) for i in range(10)) + ''.join(random.choice(uppercase) for i in range(10)) 

    return shuffle_word(numbersAndLetters)

def encrypt(text):
    key = ENCRYPTION_KEY
    fernet = Fernet(key)
    return fernet.encrypt(text.encode())

@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route("/add-user", methods=["POST"])
def add_user():
        all_users = User.query.all()

        for x in all_users:
            if (x.user_name == request.json["user_name"]):
                raise Exception("A user with this name already exists.")

        user_name = request.json["user_name"]
        user_password = bcrypt.hashpw(password=request.json["user_password"].encode('utf-8'), salt=bcrypt.gensalt())

        password_bank_record = PasswordBank(user_password)

        db.session.add(password_bank_record)
        db.session.commit()

        user = User(user_name, password_bank_record.password_bank_id)

        db.session.add(user)
        db.session.commit()

        CreatedUser = User.query.get(user.user_id) 
        return user_schema.jsonify(CreatedUser)

@app.route("/login", methods=["POST"])
def login():
    user_name = request.json["user_name"]
    user_password = request.json["user_password"]
    user_id = 0

    all_users = User.query.all()

    for x in all_users:
        if x.user_name == user_name:
            user_id = x.user_id

    if user_id == 0:
        return '', 500

    user = User.query.get(user_id)
    password_bank = PasswordBank.query.get(user.password_bank_id)

    if bcrypt.checkpw(user_password.encode('utf-8'), password_bank.password_hash):
        return '', 200
    else:
        return '', 401

@app.route("/user/<id>", methods=["PUT"])
def update_user(id):
    user = User.query.get(id)

    new_user_name = request.json["user_name"]
    new_user_password = bcrypt.hashpw(password=request.json["user_password"].encode('utf-8'), salt=bcrypt.gensalt())

    password_bank = PasswordBank.query.get(user.password_bank_id)
    password_bank.password_hash = new_user_password

    user.user_name = new_user_name

    db.session.commit()
    return user_schema.jsonify(user)

@app.route("/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify("User deleted")

@app.route("/add-website", methods=["POST"])
def add_website():
    website_name = request.json["website_name"]
    website_username = request.json["website_username"]
    website_password = create_password()

    user = User.query.get(1)
    encrypted_website_name = encrypt(website_name)
    encrypted_website_username = encrypt(website_username)
    encrypted_website_password = encrypt(website_password)

    website = Website(user.user_id, encrypted_website_name, encrypted_website_username, encrypted_website_password)
    db.session.add(website)
    db.session.commit()

    created_website = Website.query.get(website.website_id)
    return website_schema.jsonify(created_website)

@app.route("/get-websites", methods=["GET"])
def get_websites():
    websites = Website.query.all()
    return websites_schema.jsonify(websites)

@app.route("/delete-website/<id>", methods=["DELETE"])
def delete_website(id):
    website = Website.query.get(id)

    db.session.delete(website)
    db.session.commit()

    return jsonify('Website deleted')

if __name__ == "__main__":
        app.debug = True
        app.run()