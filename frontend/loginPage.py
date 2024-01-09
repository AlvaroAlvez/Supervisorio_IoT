from flask import Flask, request, render_template, redirect, url_for
import bcrypt


app = Flask('__name__')

with open('credentials.txt', 'r') as file:
     username = file.readline().strip()
     password = file.readline().strip()

@app.route('/')
def login_page():
    return render_template('loginPage.html')
