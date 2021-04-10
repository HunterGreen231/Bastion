import bcrypt
import requests
import json
from cryptography.fernet import Fernet
from Secrets import *

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

	response = requests.post("http://localhost:5000/login", json=data)
	response_status_code = response.status_code

	if response_status_code == 200:
		print("\nAccess granted! \n")
		ShowLoggedInPage()
	elif response_status_code == 401:
		print("Wrong password")
		Start()
	elif response_status_code == 500:
		print("Username does not exist")
		Start()
	else:
		print("Something went wrong with the login request:")
		Start()

def decrypt(text):
    key = ENCRYPTION_KEY
    fernet = Fernet(key)
    return fernet.decrypt(text).decode()

def AddNewWebsite():
	website_name = input("Enter website name: \n")
	website_username = input("Enter website username: \n")

	data = {
		"website_name": website_name,
		"website_username": website_username,
	}

	response = requests.post("http://localhost:5000/add-website", json=data)
	if response.status_code == 200:
		print("Successfully added site! Please search for the new site to obtain the generated password.")
	else:
		print("Something went wrong adding the site. Look in console.")
	ShowLoggedInPage()

def SearchForWebsite():
	search_input = input("Enter site name: \n")

	response = requests.get("http://localhost:5000/get-websites")

	for site in response.json():
			if decrypt(site["website_name"].encode('utf-8')) == search_input:
				print("\n")
				for data_point, data in site.items():
					if data_point == "user_id":
						print(f'{data_point}: {data}')
					elif data_point == "website_id":
						print(f'{data_point}: {data}')
					else:
						print(f'{data_point}: {decrypt(data.encode())}')

	ShowLoggedInPage()

def DeleteWebsite():
	website_id = input("input website id to delete: \n")

	response = requests.delete(f"http://localhost:5000/delete-website/{website_id}")

	print(response.json())
	ShowLoggedInPage()

def ShowLoggedInPage():
	logged_in_input = input("Would you like to add a new website(1), search for a website(2), delete a website(3), quit(4): \n")

	if logged_in_input == "1":
		AddNewWebsite()
	elif logged_in_input == "2":
		SearchForWebsite()
	elif logged_in_input == "3":
		DeleteWebsite()
	elif logged_in_input == "4":
		exit()

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