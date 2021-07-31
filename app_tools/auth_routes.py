from app_tools import app
from flask import render_template, request, redirect, url_for, flash, make_response, session, abort, send_from_directory
from flask_login import login_user, current_user, logout_user
from .models import User, Formation, db, User_detail, Promo, Folder_type, Step, Promo_user, UserRoles, Document_type, Document_folder, Folder_promo, Document_user, Status
from .forms import LoginForm, SignupForm, User_createForm, EditProfileForm, CheckEmailForm, PasswordForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import login_required, roles_required, SQLAlchemyAdapter, UserManager, UserMixin
from werkzeug.utils import secure_filename
import imghdr
import os



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/')
def index():
    return render_template('index.html')


#enregistrement du user apres la reation de son email=>il cree un password
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        #print('user', user)
        #print('user', user.password)
        if user.password != '':
            #print('user not none')
            flash('tu es deja enregistré!', "warning")
            return redirect(url_for('login'))
        password = app.user_manager.hash_password(form.password.data)
        #print('password', password)
        user.password = password
        #db.session.add(user.password)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', "info")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form )



#login lorsque le user a mail et password. Renvoie soit au user board soit a l'admin board
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not app.user_manager.verify_password(form.password.data, user):
            flash('Email ou mot de passe invalide', "warning")
            return redirect(url_for('login'))
        login_user(user)
        exists = db.session.query(UserRoles.id).filter_by(user_id=user.id, role_id=2).scalar() is not None
        if exists == True:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('login.html', form=form)


#deconnexion
####=>bien le positionner
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous êtes bien déconnectés", "info")
    return redirect(url_for('login'))


#mise a jour d'un password pour user connecte 
@app.route('/update/password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = PasswordForm()
    if form.validate_on_submit():
        user_logged = current_user.id
        user = User.query.filter_by(id=user_logged).first_or_404()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Password registered!', "info")
        return redirect(url_for('user'))
    return render_template('update_password.html', title='Sign up', form=form )


if __name__ == '__main__':
    app.run()
