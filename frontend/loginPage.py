from flask import Flask, request, render_template, redirect, url_for
import bcrypt


app = Flask('__name__')

with open('credentials.txt', 'r') as file:
     username = file.readline().strip()
     password = file.readline().strip()

@app.route('/')
def login_page():
    return render_template('loginPage.html')

@app.route('/login', methods=['POST'])
def login():
    # ... verificação do login ...
    return redirect(url_for('dashboard2'))  # Redireciona para o dashboard

@app.route('/dashboard2')
def dashboard():
    return render_template('dashboard2.html')  # essa é a página com as bombas animadas


