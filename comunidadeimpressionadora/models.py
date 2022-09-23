from comunidadeimpressionadora import db, login_manager
from datetime import date, datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id_user):
    return Usuario.query.get(int(id_user))


class Usuario(db.Model, UserMixin):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    fullname = db.Column(db.String(50), nullable=True, default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    passwd = db.Column(db.String(30), nullable=False)
    birth_date = db.Column(db.Date, default=None)
    profile_pic = db.Column(db.String(2000), default='default.jpg')
    cursos = db.Column(db.String(100), nullable=False, default='Não informado')
    posts = db.relationship('Post', backref='autor', lazy=True)

    def count_posts(self):
        return len(self.posts)

    def get_id(self):
        return self.id_user


class Post(db.Model):
    id_post = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_user = db.Column(db.Integer, db.ForeignKey('usuario.id_user'), nullable=False)

