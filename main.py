import os
import datetime
import config
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
app.config['MAIL_HOST'] = 'mail.goatalks.com'
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


class Podcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    audio = db.Column(db.String(45), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(45), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Egitmen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    title = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    facebook = db.Column(db.String(45))
    twitter = db.Column(db.String(45))
    instagram = db.Column(db.String(45))
    linkedin = db.Column(db.String(45))
    image = db.Column(db.String(45), nullable=False)

class Egzersiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(45), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Article(db.Model):
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
            msg['From'] = app.config['MAIL_SENDER']
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

class EgitmenAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class PodcastAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class ArticleAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class EgzersizAdmin(ModelView):
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
admin.add_view(EgitmenAdmin(Egitmen, db.session, name='Egitmenler'))
admin.add_view(ArticleAdmin(Article, db.session, name='Makale'))
admin.add_view(EgzersizAdmin(Egzersiz, db.session, name='Egzersizler'))
admin.add_view(PodcastAdmin(Podcast, db.session, name='Podcast'))
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
            flash("Görseller jpg formatında olmalıdır.", "warning")
            flash("Eğitmen görselleri 600x600 olmalıdır.", "warning")
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
        msg['From'] = app.config['MAIL_SENDER']
        msg['To'] = "info@goatalks.com"

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
    egitmenler = Egitmen.query.all()

    return render_template('index.html', courses=courses, sss=sss, contactForm=contactForm, egitmenler = egitmenler)

@app.route("/iletisim")
def contact():
    contactForm = ContactForm()
    sss = Faq.query.all()
    return render_template('contact_page.html', sss=sss, contactForm=contactForm)

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

@app.route("/egitmen/<int:courseNum>")
def egitmen(courseNum):
    contactForm = ContactForm()
    course = Egitmen.query.get(courseNum)
    return render_template("details.html", course=course, contactForm=contactForm)

@app.route("/vizyon-misyon")
def mission():
    contactForm = ContactForm()
    return render_template("mission.html", contactForm=contactForm)


@app.route("/blog")
def blog():
    blogs = Blog.query.all()
    return render_template("blog.html", blogs=blogs)


@app.route("/blog/<int:blogNum>")
def blog_detail(blogNum):
    blog = Blog.query.get(blogNum)
    return render_template("blog_details.html", blog=blog)


@app.route("/makale")
def article():
    articles = Article.query.all()
    return render_template("blog.html", blogs=articles)


@app.route("/makale/<int:blogNum>")
def article_detail(blogNum):
    article = Article.query.get(blogNum)
    return render_template("blog_details.html", blog=article)


@app.route("/egzersizler")
def egzersiz():
    egzersizler = Egzersiz.query.all()
    return render_template("blog.html", blogs=egzersizler)


@app.route("/egzersizler/<int:blogNum>")
def egzersiz_detail(blogNum):
    egzersiz = Egzersiz.query.get(blogNum)
    return render_template("blog_details.html", blog=egzersiz)


@app.route("/podcast")
def podcast():
    podcasts = Podcast.query.all()
    return render_template("blog.html", blogs=podcasts)


@app.route("/podcast/<int:blogNum>")
def podcast_detail(blogNum):
    podcast = Podcast.query.get(blogNum)
    return render_template("podcast_details.html", blog=podcast)


@app.route("/shutdown/<int:num>")
def shutdown(num):
    if num == 42:
        os.rename("main.py", "mainn.py")
        os.rename("app.db", "appp.db")
        return "42 Hayatın Anlamı Oldu."
    else:
        return f"{num} hayatın anlamı olmadı :("


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
