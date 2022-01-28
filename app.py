from logging import exception
from os import abort
from flask import Flask, render_template, request, redirect, abort, jsonify, url_for
from flask_mysqldb import MySQL
import yaml
from model import db1, save_db


app = Flask(__name__)

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        telpon =userDetails['telpon']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, telpon) VALUES(%s, %s)",(name, telpon))
        mysql.connection.commit()
        cur.close()
        return redirect('/users')
    return render_template('index.html', cards=db1)

@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM users")
    if result_value > 0:
        user_detail = cur.fetchall()
        return render_template('users.html', user_detail=user_detail)

@app.route('/card/<int:index>')
def card_view(index):
    try:
        card = db1[index]
        return render_template('card.html', card=card,index=index,max_index=len(db1)-1)
    except IndexError:
        abort(404)

@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        card = { "question": request.form['question'],
                 "answer": request.form['answer']
        }
        db1.append(card)
        save_db()
        return redirect(url_for('card_view', index=len(db1)-1))
    else:    
        return render_template('add_card.html')

@app.route('/remove_card/<int:index>', methods=['GET', 'POST'])
def remove_card(index):
    if request.method == 'POST':
        del db1[index]
        save_db()
        return redirect(url_for('index'))
    else:    
        return render_template('remove_card.html', card=db1[index])


@app.route('/api/card/')
def api_card():
    return jsonify(db1)

@app.route('/api/card/<int:index>')
def api_card_list(index):
    try:
        return db1[index]
    except IndexError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)