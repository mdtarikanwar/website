# importing required modules.
import json
import math
import os
from mysql import connector
from datetime import datetime

from flask import Flask, render_template, request, session, redirect
from werkzeug.utils import secure_filename


# stabilised connection to the Mysql
con = connector.connect(user="root",
                        password="Belsarnifu30@",
                        host="localhost",
                        database="my_tables")
# making a cursor for the execution of sql command.
cr = con.cursor()

# opening config.json file, this json file contains many attributes for the web pages.
with open("config.json", "r") as f:
    params = json.load(f)["params"]

# creating an object of Flask class (Flask App).
app = Flask(__name__)

# setting the secret_key attribute of app.
app.secret_key = 'super-secrer-key'

# setting the folder where all image file will be uploaded, which will come from json file.
app.config['UPLOAD_FOLDER'] = params['upload_location']


# making a route for the Hone page.
@app.route("/")
def index():
    cr.execute("select * from posts;")

    posts = tuple(cr)

    last = math.ceil(len(posts) / int(params['no_of_post']))

    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[
            (page - 1) * int(params['no_of_post']):(page - 1) * int(params['no_of_post']) + int(params['no_of_post'])]

    if page == 1:
        prev = "#"
        next = '/?page=' + str(page + 1)
    elif page == last:
        next = "#"
        prev = '/?page=' + str(page - 1)
    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


# making a route for contact page.
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''
        date entry to the database
        Name , email, phone ,mes , date
        '''
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        print(name, email, phone, message)

        cr.execute("insert into contacts(Name, Email, Phone, Date, Message) values('"+name+"', '"+email+"', '"+phone+"', '"+str(datetime.now())+"', '"+message+"')")
        con.commit()

    return render_template('contact.html', params=params)


# making a route for about page.
@app.route("/about")
def about():
    return render_template('about.html', params=params)


# making a route for posts page.
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    cr.execute("select * from posts where slug='"+post_slug+"'")
    post = tuple(cr)[0]
    return render_template('post.html', params=params, post=post)


# making a route for admin page.
@app.route("/admin", methods=['GET', 'POST'])
def login():
    cr.execute("select * from posts;")
    posts = tuple(cr)

    if 'user' in session and session['user'] == params['admin_user_id']:
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpassword = request.form.get('upass')
        if username == params['admin_user_id'] and userpassword == params['admin_password']:
            session['user'] = username
            return render_template("dashboard.html", params=params, posts=posts)
        else:
            return render_template('login.html', params=params)
    else:
        return render_template('login.html', params=params)


# making a route for logout page, which will redirect to the home page.
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')


# making a route for edit page.
@app.route('/edit/<string:S_No>', methods=['GET', 'POST'])
def edit(S_No):
    if 'user' in session and session['user'] == params['admin_user_id']:
        string = ''
        if request.method == 'POST':
            box_title = request.form.get('title')
            Tagline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            image_file = request.form.get('img_file')
            date = datetime.now()

            if S_No == '0':

                cr.execute("insert into posts(Title, Tagline, Content, slug, Img_file) values('"+box_title+"', '"+Tagline+"', '"+content+"', '"+slug+"', '"+image_file+"')")

                con.commit()
                string = 'Post added Successfully!'

            else:
                cr.execute(f"update posts set Title='{box_title}', Tagline = '{Tagline}', Content = '{content}', slug "
                           f"= '{slug}', Img_file = '{image_file}', date = '{date}' where S_No='{S_No}'")
                con.commit()

        cr.execute("select * from posts where S_No='" + S_No + "'")

        try:
            post = tuple(cr)[0]

        except IndexError:
            post = tuple(cr)

        return render_template("edit.html", params=params, post=post, S_No=S_No, mystr=string)


# making a route for delete page, which will redirect to the admin page.
@app.route("/delete/<string:S_No>", methods=['GET', 'POST'])
def delete(S_No):
    if 'user' in session and session['user'] == params['admin_user_id']:
        cr.execute(f"delete from posts where S_No='{S_No}'")
        con.commit()

        return redirect('/admin')


# making a route for file upload page, which will redirect to the admin page after file uploaded.
@app.route("/uploader", methods=['POST', 'GET'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user_id']:
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return redirect("/admin")


app.run(debug=True)
