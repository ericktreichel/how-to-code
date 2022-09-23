from flask import render_template, request, redirect, flash, url_for, abort
from comunidadeimpressionadora import app, db, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditProfile, FormNewPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
import secrets
import os


@app.route("/")
def home():
    posts = Post.query.order_by(Post.id_post.desc())
    return render_template('home.html', posts=posts)


@app.route("/contato")
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()

    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criar_conta = FormCriarConta()

    if form_login.validate_on_submit() and 'submit_login_button' in request.form:
        user_log = Usuario.query.filter_by(email=form_login.email.data).first()
        if user_log and bcrypt.check_password_hash(user_log.passwd, form_login.senha.data):
            # Login autorizado
            login_user(user_log, remember=form_login.lembrar_sessao.data)
            # Msg de login realizado com sucesso
            flash(f'Login successfull. You are now logged {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f"Login attempt failed. E-mail ({form_login.email.data}) and password don't match", 'alert-danger')

    if form_criar_conta.validate_on_submit() and 'submit_create_button' in request.form:
        # criar o usuário
        passwd_crypt = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(username=form_criar_conta.username.data, email=form_criar_conta.email.data, passwd=passwd_crypt)
        # adicionar a session e commit
        db.session.add(usuario)
        db.session.commit()

        # Msg de conta criada com sucesso
        flash(f"{form_login.email.data} account's create successfully!", 'alert-success')
        return redirect(url_for('home'))

    return render_template('login.html', form_login=form_login, form_criar_conta=form_criar_conta)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'Logout successfully', 'alert-primary')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    profile_pic = url_for('static', filename=f'profile_pictures/{current_user.profile_pic}')
    return render_template('perfil.html', profile_pic=profile_pic)


# função que recebe e tratar novas profile pictures
def save_profile_pic(picture):
    # adicionar cód aleatório no nome da imagem
    cod = secrets.token_hex(8)
    nome, extensao = os.path.splitext(picture.filename)
    final_pic_name = nome + cod + extensao
    full_path = os.path.join(app.root_path, 'static/profile_pictures', final_pic_name)
    # resize picture
    size = (350, 350)
    resized_pic = Image.open(picture)
    resized_pic.thumbnail(size)
    # salvar imagem na pasta profile_pictures
    resized_pic.save(full_path)
    # mudar o campo profile_pic para a nova imagem
    return final_pic_name


# função que trata cursos marcados
def update_cursos(form):
    lista_cursos = []
    for field in form:
        if 'curso_' in field.name:
            if field.data:
                lista_cursos.append(field.label.text)
    return ';'.join(lista_cursos)


@app.route('/perfil/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form_edit = FormEditProfile()
    if form_edit.validate_on_submit():
        current_user.fullname = form_edit.fullname.data
        current_user.email = form_edit.email.data
        current_user.username = form_edit.username.data
        current_user.birth_date = form_edit.birth_date.data
        # checar se ele adicinou uma foto no formulário
        if form_edit.profile_pic.data:
            pic_name = save_profile_pic(form_edit.profile_pic.data)
            current_user.profile_pic = pic_name
        if form_edit.remove_pic.data == "I don't want a picture":
            current_user.profile_pic = 'default.jpg'
        current_user.cursos = update_cursos(form_edit)
        db.session.commit()
        flash(f'Profile updated successfully!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form_edit.fullname.data = current_user.fullname
        form_edit.username.data = current_user.username
        form_edit.email.data = current_user.email
        form_edit.birth_date.data = current_user.birth_date
    profile_pic = url_for('static', filename=f'profile_pictures/{current_user.profile_pic}')
    return render_template('editprofile.html', profile_pic=profile_pic, form_edit=form_edit)


@app.route('/post/newpost', methods=['GET', 'POST'])
@login_required
def new_post():
    form_new_post = FormNewPost()
    if form_new_post.validate_on_submit():
        post = Post(title=form_new_post.title.data, body=form_new_post.body.data, autor=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post successfully submitted!", 'alert-success')
        return redirect((url_for('home')))
    return render_template('newpost.html', form_new_post=form_new_post)

@app.route('/post/<id_post>', methods=['GET', 'POST'])
@login_required
def show_post(id_post):
    post = Post.query.get(id_post)
    if current_user == post.autor:
        # como os campos para editar o post são os mesmos para criar um post, vou reaproveitar o formulário de new post
        form_edit_post = FormNewPost()
        if request.method == 'GET':
            form_edit_post.title.data = post.title
            form_edit_post.body.data = post.body
        if form_edit_post.validate_on_submit():
            post.title = form_edit_post.title.data
            post.body = form_edit_post.body.data
            db.session.commit()
            flash('Changes saved successfully', 'alert-info')
    else:
        # para evitar um erro caso o current_user seja diferente do post.autor eu coloco esse else aqui
        form_edit_post = None
    return render_template('post.html', post=post, form_edit_post=form_edit_post)


@app.route('/post/<id_post>/remove', methods=['GET', 'POST'])
@login_required
def remove_post(id_post):
    post = Post.query.get(id_post)
    if current_user == post.autor:
        db.session.delete(post)
        db.session.commit()
        flash('Post successfully removed', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
