from flask import Flask, render_template, request, send_from_directory, url_for, flash, redirect
import psycopg2
import os
from werkzeug.utils import secure_filename
import urllib.request

hostname = 'localhost'
database = 'univers'
username = 'postgres'
pwd = '291627'
port_id = 5432


conn = psycopg2.connect(
    host=hostname,
    dbname=database,
    user=username,
    password=pwd,
    port=port_id
)
cur = conn.cursor()

create_script = ''' CREATE TABLE IF NOT EXISTS post (
Email varchar(40)  NOT NULL,
Subject varchar(50),
Message varchar(150)
) '''
cur.execute(create_script)
conn.commit()

create_script = ''' CREATE TABLE IF NOT EXISTS register (
Name varchar(40)  NOT NULL,
Email varchar(50),
Password varchar(50)
) '''
cur.execute(create_script)
conn.commit()


create_script = ''' SELECT Email, Subject, Message FROM post;'''
cur.execute(create_script)
conn.commit()
people = cur.fetchall()
conn.commit()

app = Flask(__name__)

UPLOAD_FOLDER = 'static/files/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



@app.route('/', methods = ['GET', 'POST'])
def main():
    return render_template('index.html')

@app.route('/message', methods = ['GET', 'POST'])
def message():
    if request.method == 'POST':
        Email = request.form["Email"]
        Subject = request.form["Subject"]
        Message = request.form['Message']
        insert_into = 'INSERT INTO post VALUES (%s, %s, %s)'
        insert_values = (Email, Subject, Message)
        cur.execute(insert_into, insert_values)
        conn.commit()
        return render_template('index.html')
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    return render_template('components.html')
@app.route('/sigin', methods=['GET','POST'])
def sig():
    if request.method == 'POST':
        Name = request.form['Name']
        Email = request.form['Email']
        Password = request.form['Password']
        insert_into = 'INSERT INTO register VALUES (%s, %s, %s)'
        insert_values = (Name,Email, Password)
        cur.execute(insert_into, insert_values)
        conn.commit()
        return render_template('sigin.html')
    return render_template('sigin.html')
@app.route('/panel', methods = ['GET','POST'])
def panel():
    txt = "Вы неправильно ввели данные!"
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']

        select = 'SELECT Email, Password, Name FROM register'
        cur.execute(select)
        select_all = cur.fetchall()
        print(select_all)
        for i in select_all:
            check_one = False
            if Email == i[0]:
                check_one = True
                Name = i[2]
                break
        for i in select_all:
            check_two = False
            if Password == i[1]:
                check_two = True
                break
        if check_one == check_two:
            return render_template("create.html", people=people, Name=Name)
        return render_template("sigin.html", word=txt)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/subm')
def home():
    return render_template('post.html')


@app.route('/subm', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image successfully uploaded and displayed below')
        return render_template('post.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='files/' + filename), code=301)

if __name__ == '__main__':
    app.run(debug=True)