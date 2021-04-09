import bcrypt
import requests
import json

def CreateUser():
	user_name = input("Enter your user name: \n")
	user_password = input("Enter your password: \n")

	data = {
		"user_name": user_name,
		"user_password": user_password
	}

	try:
		response = requests.post("http://localhost:5000/add-user", json=data)
	except AssertionError as error:
		print(error)
		Start()

	print(response.json())

def GetUsers():
	response = requests.get("http://localhost:5000/users")

	print(response.json())

def DeleteUser():
	user_id = input("Enter user_id of user you want to delete: \n")

	response = requests.delete(f"http://localhost:5000/user/{user_id}")

	print(response.json())

def Login():
	user_name = input("Enter user name: \n")
	user_password = input("Enter password: \n")

	data = {
		"user_name": user_name,
		"user_password": user_password
	}

	message = ""
	response = requests.post("http://localhost:5000/login", json=data).json()
	for key, value in response.items():
		if key == "Message":
			message = value

	if message == "Access Granted":
		ShowSiteData()
	elif message == "Wrong Password":
		print("Wrong password")
		Start()
	elif message == "null":
		print("No user with that user name.")
		Start()
	else:
		print("Something went wrong with the login request:")
		print(response)
		Start()

def ShowSiteData():
	print("Display site data here")

def Start():
	initial_input = input("Would you like to login(1), create a new user(2), edit a user(3), delete a user(4), view users(5), quit(6): \n")

	if initial_input == "1":
		Login()
	elif initial_input == "2":
		CreateUser()
	elif initial_input == "4":
		DeleteUser()
	elif initial_input == "5":
		GetUsers()
	elif initial_input == "6":
		exit()
	else:
		print("No valid option selected")
		Start()

Start()