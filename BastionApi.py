from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
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
        fields = ("user_id", "user_name", "password_bank_id")

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
        return {"Message": "null"}

    user = User.query.get(user_id)
    password_bank = PasswordBank.query.get(user.password_bank_id)

    if bcrypt.checkpw(user_password.encode('utf-8'), password_bank.password_hash):
        return {"Message": "Access Granted"}
    else:
        return {"Message": "Wrong Password"}

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

if __name__ == "__main__":
        app.debug = True
        app.run()