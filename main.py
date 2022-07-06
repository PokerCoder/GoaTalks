from crypt import methods
import os
import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import config

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

app.config['MAIL_SENDER'] = config.mail
app.config['MAIL_PASSWORD'] = config.mail_password
app.config['MAIL_HOST'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587


class ContactForm(FlaskForm):
    name = StringField("Name", [validators.InputRequired()])
    email = StringField("Email", [validators.Email()])
    subject = StringField("Subject", [validators.InputRequired()])
    message = TextAreaField("Message", [validators.InputRequired()])


class ContactHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    email = db.Column(db.String(140))
    subject = db.Column(db.String(140))
    message = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Faq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(500), nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(45), nullable=False)
    show = db.Column(db.Boolean)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(45), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(45), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    password = db.Column(db.String(45))


class FileAdminView(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    can_mkdir = False


class MyHomeView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    @expose('/', methods=["GET", "POST"])
    def index(self):
        subscribers = Subscriber.query.all()

        if request.method == "POST":

            recipients = []
            for i in subscribers:
                recipients.append(i.email)

            subject = request.form['subject']

            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = "noreply"
            msg['To'] = ", ".join(recipients)

            content = str(request.form['content'])

            html_content = MIMEText(content, 'html')

            msg.set_content(html_content)

            with smtplib.SMTP(app.config['MAIL_HOST'], app.config['MAIL_PORT']) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(app.config['MAIL_SENDER'],
                           app.config['MAIL_PASSWORD'])
                smtp.send_message(msg)

            flash("Toplu mail gönderilmiştir", "success")
            return redirect(url_for('admin.index'))

        return self.render('admin/index.html', subscribers=subscribers)


class ContactAdmin(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    can_edit = False
    can_create = False

class BlogAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class FaqAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class CourseAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, name='Admin Panel',
              template_mode='bootstrap3', index_view=MyHomeView())
admin.add_view(FileAdminView(
    app.config['UPLOAD_FOLDER'], '/static/', name='Dosyalar'))
admin.add_view(CourseAdmin(Course, db.session, name='Eğitimler'))
admin.add_view(FaqAdmin(Faq, db.session, name='SSS'))
admin.add_view(ContactAdmin(ContactHistory, db.session, name='İletişim'))
admin.add_view(BlogAdmin(Blog, db.session, name='Blog'))
admin.add_link(MenuLink(name='Çıkış Yap', category='', url="/logout"))

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username, password=password).first()

        if user:
            login_user(user)
            return redirect(url_for("admin.index"))
        else:
            flash("kullanıcı adı veya şifre yanlış.", "error")
            return redirect(url_for("login"))


    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/get-contact", methods=["POST", "GET"])
def get_contact():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        msg = EmailMessage()
        msg['Subject'] = "Goatalks Web İletişim Formu"
        msg['From'] = "noreply"
        msg['To'] = "erdinc_akgun@hotmail.com"

        content = f"""
        
        Müşteri Adı: {name}

        Müşteri Mail Adresi: {email}

        Konu: {subject}

        Mesaj: {message}

        """

        msg.set_content(content)

        with smtplib.SMTP(app.config['MAIL_HOST'], app.config['MAIL_PORT']) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_PASSWORD'])
            smtp.send_message(msg)

        record = ContactHistory(name=name, email=email,
                                subject=subject, message=message)

        db.session.add(record)
        db.session.commit()

        flash("Bizimle iletişime geçtiğiniz için teşekkürler.", "success")
        return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        email = request.form["email"]
        subscriber = Subscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()
        flash("Abone olduğunuz için teşekkürler.", "success")
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/")
def index():

    contactForm = ContactForm()
    courses = Course.query.filter_by(show=True).all()
    sss = Faq.query.all()

    return render_template('index.html', courses=courses, sss=sss, contactForm=contactForm)

@app.route("/egitimler")
def courses():
    courses = Course.query.all()
    contactForm = ContactForm()
    return render_template("courses.html", courses=courses, contactForm=contactForm)

@app.route("/egitim/<int:courseNum>")
def detail(courseNum):
    contactForm = ContactForm()
    course = Course.query.get(courseNum)
    return render_template("details.html", course=course, contactForm=contactForm)

@app.route("/blog/<int:blogNum>")
def blog_detail(blogNum):
    blog = Blog.query.get(blogNum)
    return render_template("blog_details.html", blog=blog)

@app.route("/vizyon-misyon")
def mission():
    contactForm = ContactForm()
    return render_template("mission.html", contactForm=contactForm)


@app.route("/blog")
def blog():
    blogs = Blog.query.all()
    return render_template("blog.html", blogs=blogs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
