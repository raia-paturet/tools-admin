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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/uploads/<path:filepath>')
def uploading(filepath):
    promo_dirname = os.path.dirname(filepath)
    dirpath = os.path.join("..", app.config['UPLOAD_FOLDER'], promo_dirname)
    filename = os.path.basename(filepath)
    return send_from_directory(directory=dirpath, filename=filename, as_attachment=True)


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

#acces au dashboard du user.//si il a pas encore renseigne ses infos => redirection vers user_register
@app.route('/user/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    user_id = current_user.id
    exists = db.session.query(User_detail.firstname).filter_by(user_id=user_id).scalar() is not None
    if exists == False:
        return redirect(url_for('user_register'))
    user_detail = User_detail.query.filter_by(user_id=user_id).first_or_404()
    promo_user = Promo_user.query.filter_by(user_id=user_id).first_or_404()
    all_promo_folders = Folder_promo.query.filter_by(promo_id=promo_user.promo_id).all()
    all_docs_user = Document_user.query.filter_by(user_id=user_id).all()
    all_documents_folder = Document_folder.query.all()
    test1 = Document_user.query.filter_by(user_id=user_id).with_entities(Document_user.document_type_id).all()
    test = []
    for x in test1:
        test.append(x[0])
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part', "warning")
            return redirect(request.url)
        if 'file' in request.files:
            file = request.files['file']
            date = datetime.now()
            document_type_id = request.form['document']
            
            if file.filename == '':
                flash('No selected file', "warning")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                directory = promo_user.promo.formation.name+ "_" +promo_user.promo.iteration
                filename = str(user_detail.lastname)+ "_" +str(user_id)+ "_" + filename
 
                cwd = os.getcwd()
                print("cwd", cwd)

                ###=>1 enregistre le fichier sur le serveur(mais pas dans la db)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], directory, filename))

                ###=>2 enregistre le fichier  dans la db
                exists = db.session.query(Document_user.id).filter_by(user_id=user_id, document_type_id=document_type_id).scalar() is not None
                if exists:
                    docs_user = Document_user.query.filter_by(user_id=user_id, document_type_id=document_type_id).first_or_404()
                    print("test", docs_user)
                    document_user = Document_user.query.filter_by(id=docs_user.id).first_or_404()
                    document_user.file = directory+ "/" +filename
                    document_user.datetime = date
                    document_user.status = 'status2'
                    db.session.commit()
                    flash('fichier bien enregistré', "info")
                else:
                    uploaded_file = Document_user(user_id=user_id, file=filename, datetime=date, document_type_id=document_type_id, status='status2')
                    db.session.add(uploaded_file)
                    db.session.commit()
                    flash('fichier bien enregistré', "info")
            else:
                flash('ce fichier ne correspond pas essayer avec un .jpg ou .pdf', "warning")

    
    return render_template(
        'user_dashboard.html', user_detail_object=user_detail, user_detail=user_detail,
     all_promo_folders=all_promo_folders, promo_user=promo_user, all_docs_user=all_docs_user,
     all_documents_folder=all_documents_folder, test=test
     )


@app.route('/user/folder/<folder_id>', endpoint='<folder_id>', methods=['GET','POST'])
def user_upload_file(folder_id):
    user_id = current_user.id
    user_detail = User_detail.query.filter_by(user_id=user_id).first_or_404()
    folder_id = folder_id
    promo_user = Promo_user.query.filter_by(user_id=user_id).first_or_404()
    all_promo_folders = Folder_promo.query.filter_by(promo_id=promo_user.promo_id).all()
    all_docs_user = Document_user.query.filter_by(user_id=user_id).all()
    all_documents_folder = Document_folder.query.filter_by(folder_type_id=folder_id).all()

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part', "warning")
            return redirect(request.url)
        if 'file' in request.files:
            file = request.files['file']
            date = datetime.now()
            document_type_id = request.form['document']
            
            if file.filename == '':
                flash('No selected file', "warning")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                directory = promo_user.promo.formation.name+ "_" +promo_user.promo.iteration
                filename = str(user_detail.lastname)+ "_" +str(user_id)+ "_" + filename
 
                cwd = os.getcwd()
                print("cwd", cwd)

                ###=>1 enregistre le fichier sur le serveur(mais pas dans la db)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], directory, filename))

                ###=>2 enregistre le fichier  dans la db
                exists = db.session.query(Document_user.id).filter_by(user_id=user_id, document_type_id=document_type_id).scalar() is not None
                if exists:
                    docs_user = Document_user.query.filter_by(user_id=user_id, document_type_id=document_type_id).first_or_404()
                    print("test", docs_user)
                    document_user = Document_user.query.filter_by(id=docs_user.id).first_or_404()
                    document_user.file = directory+ "/" +filename
                    document_user.datetime = date
                    document_user.status = 'status2'
                    db.session.commit()
                    flash('fichier bien enregistré', "info")
                else:
                    uploaded_file = Document_user(user_id=user_id, file=filename, datetime=date, document_type_id=document_type_id, status='status2')
                    db.session.add(uploaded_file)
                    db.session.commit()
                    flash('fichier bien enregistré', "info")
            else:
                flash('ce fichier ne correspond pas essayer avec un .jpg ou .pdf', "warning")

    return render_template(
        'user_upload.html', all_documents_folder=all_documents_folder,
        all_promo_folders=all_promo_folders, all_docs_user=all_docs_user,
        promo_user=promo_user, user_detail=user_detail )


#mise a jour du profil user par le user
###=>voir pour le mail...
@app.route('/update/profile', methods=['GET', 'POST'])
@login_required
def user_update_profile():
    user_id = current_user.id
    form = EditProfileForm()
    if form.validate_on_submit():
        user_detail = User_detail.query.filter_by(user_id=user_id).first_or_404()
        user_detail.user_id = user_id
        user_detail.firstname = form.firstname.data
        user_detail.lastname = form.lastname.data
        user_detail.address = form.address.data
        user_detail.city_code = form.city_code.data
        user_detail.city = form.city.data
        user_detail.phone = form.phone.data
        db.session.commit()
        flash('Your changes have been saved.', "info")
        return redirect(url_for('user_dashboard'))
    elif request.method == 'GET':
        user_detail = User_detail.query.filter_by(user_id=user_id).first_or_404()
        form.firstname.data = user_detail.firstname
        form.lastname.data = user_detail.lastname
        form.address.data = user_detail.address
        form.city_code.data = user_detail.city_code
        form.city.data = user_detail.city
        form.phone.data = user_detail.phone
    return render_template('user_update_profile.html', form=form)

#a la premiere connexion du user, il arrive sur cette page pour enregistrer ses donnees
@app.route('/user/register', methods=['GET', 'POST'])
@login_required
def user_register():
    form = EditProfileForm()
    if form.validate_on_submit():
        user_id = current_user.id
        user_detail = User_detail.query.filter_by(user_id=user_id).first_or_404()
        user_detail.user_id = user_id
        user_detail.firstname = form.firstname.data
        user_detail.lastname=form.lastname.data
        user_detail.address=form.address.data
        user_detail.city_code= form.city_code.data
        user_detail.city= form.city.data
        user_detail.phone=form.phone.data

        db.session.commit()
        print('good')
        return redirect(url_for('user_dashboard'))
        step = User_detail.query.filter_by(user_id=current_user.id).first_or_404()
        #voir systeme d'evolution de step plus safe
        if step == 1:
            step = 4
            db.session.commit()
            flash('Your changes have been saved.', "info")
            return redirect(url_for('user_dashboard'))
        else:
            flash('Il y a une erreur dans votre dossier, merci de contacter votre contact a Matrice', "warning")
            return redirect(url_for('logout'))
        
    return render_template('user_register.html', form=form)


@app.route('/admin')
@login_required
@roles_required('admin')
def admin():
    all_users = User.query.order_by(User.email).all()
    all_users_detail = User_detail.query.order_by(User_detail.lastname).all()
    all_promos = Promo.query.order_by(Promo.formation_id).all()
    all_formations = Formation.query.order_by(Formation.name).all()
    all_documents_to_check = Document_user.query.order_by(Document_user.datetime).all()
    

    return render_template(
        'admin.html', all_users=all_users, all_promos=all_promos,
        all_users_detail=all_users_detail, all_documents_to_check=all_documents_to_check,
        )

#user cote admin
@app.route('/admin/user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_user():
    all_users = User.query.order_by(User.email).all()
    all_users_detail = User_detail.query.order_by(User_detail.lastname).all()
    all_promos = Promo.query.all()
    if request.method == 'POST':

#email_form est le formulaire de creation d'un user avec son mail et sa promo
        if 'email_form' in request.form and 'user_promo_form' in request.form:
            try:
                ## 1 : on chek et enregistre le mail
                email_form = request.form.get('email_form')
                if db.session.query(User.id).filter_by(email=email_form).scalar() is not None:
                    flash('email already exist!', "warning")
                    return render_template('admin_user.html', all_users=all_users, all_promos=all_promos)
                user = User(email=email_form)
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_user'))

                ## 2 : on lui affecte une promo et un step
            try:
                user_promo_form = request.form.get('user_promo_form')
                user_object = User.query.filter_by(email=email_form).first_or_404()
                user_promo = Promo_user(user_id=user_object.id, promo_id=user_promo_form, user_step="step1")
                db.session.add(user_promo)
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_user'))
        
                ## 3 :  on cree son profil dans user_detail
            try:
                user_detail = User_detail(user_id=user_object.id,)
                db.session.add(user_detail)
                db.session.commit()
                flash('New user registered!', "info")
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_user'))
            return redirect(url_for('admin_user'))

### user_list est la liste des etudiants=> si selectionne on ouvre la fiche individuelle de l'etudiant (=>sur la meme page?)
    return render_template('admin_user.html', all_users=all_users, all_promos=all_promos, all_users_detail=all_users_detail)


@app.route('/admin/users/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_user_card(user_id):
    user_id = user_id
    step = Step
    promo_user = Promo_user.query.filter_by(user_id=int(user_id)).first_or_404()
    user_detail_object = User_detail.query.filter_by(user_id=user_id).first_or_404()
    promo_id = promo_user.promo_id
    all_promo_folders = Folder_promo.query.filter_by(promo_id=promo_id).all()
    all_docs_user = Document_user.query.filter_by(user_id=user_id).all()
    all_documents_folder = Document_folder.query.all()
    test1 = Document_user.query.filter_by(user_id=user_id).with_entities(Document_user.document_type_id).all()
    test = []
    for x in test1:
        test.append(x[0])

    if request.method == 'POST':

        if 'user_step' in request.form:
            try:
                new_step = request.form.get('user_step')
                promo_user_object = Promo_user.query.filter_by(user_id=int(user_id)).first_or_404()
                promo_user_object.user_step = Step(new_step).name
                db.session.commit()
                return redirect(url_for('admin_user_card', user_id=user_id))
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_user_card', user_id=user_id))

        if 'doc_status' in request.form:
            try:
                new_status = request.form.get('doc_status')
                doc_user_id = request.form.get('doc_user_id')
                doc_user_object = Document_user.query.filter_by(id=int(doc_user_id)).first_or_404()
                doc_user_object.status = Status(new_status).name
                db.session.commit()
                return redirect(url_for('admin_user_card', user_id=user_id))
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_user_card', user_id=user_id))
    return render_template(
        'admin_user_card.html', user_detail_object=user_detail_object,
        promo_user=promo_user, step=step, all_promo_folders=all_promo_folders,
        all_documents_folder=all_documents_folder, all_docs_user=all_docs_user, test=test
      )


@app.route('/admin/formation', methods=["GET", "POST"])
@login_required
@roles_required('admin')
def admin_formation():
    
    all_formations = Formation.query.all()
    all_promos = Promo.query.all()

    if request.method == 'POST':

        if 'formation_name' in request.form:
            formation_name = request.form.get('formation_name')
        
            try:
                clean_formation_name = formation_name.replace(" ", "_").upper()
                exists = db.session.query(Formation.id).filter_by(name=clean_formation_name).scalar() is not None
                if exists:
                    flash("Cette formation existe deja", "warning")
                    return redirect(url_for('admin_formation'))
                else:
                    formation = Formation(
                        name = clean_formation_name,
                    )
                    db.session.add(formation)
                    db.session.commit()
                    flash("Nouvelle formation enregistrée!", "info")
                    return redirect(url_for('admin_formation'))
            except Exception as e:
                flash(str(e), "warning")

    #LAURIE => pourquoi le and ne fonctionne pas?       
        if 'iteration' and 'formation' in request.form:
            formation = request.form.get('formation')
            iteration = request.form.get('iteration')
            if iteration is None or formation == "_":
                flash('Sélectionner un formation', "warning")
                return redirect(url_for('admin_formation'))

            exists = db.session.query(Promo.id).filter_by(formation_id=formation, iteration=iteration).scalar() is not None
            
            if exists:
                flash("cette promo existe deja", "warning")
                return redirect(url_for('admin_formation'))
            else:
                try:
                    promo = Promo(
                        iteration = iteration, formation_id = formation
                    )
                    db.session.add(promo)
                    db.session.commit()
                    flash("Nouvelle promo enregistrée!", "info")
                except Exception as e:
                    flash(str(e), "warning")
                # create the formation//directory 
                cwd = os.getcwd()
                try:
                    dir_name = os.path.join(app.config['UPLOAD_FOLDER'], str(promo.formation.name+"_"+promo.iteration))
                    os.makedirs(dir_name)
                except Exception as e:
                    flash(str(e), "warning")
                else:
                    flash("Le dossier de la promo a bien été crée", "info")
                    return redirect(url_for('admin_formation'))


    return render_template('admin_formation.html', all_formations = all_formations, all_promos=all_promos)


@app.route('/admin/promo/<promo_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_promo_card(promo_id):
    promo_id = promo_id
    promo = Promo.query.filter_by(id=promo_id).first_or_404()
    all_students = Promo_user.query.filter_by(promo_id=promo_id).all()
    all_folders = Folder_type.query.all()
    all_folders_promo = Folder_promo.query.filter_by(promo_id=promo_id).all()
    if request.method == 'POST':

        if 'folders' in request.form:
            folders = request.form.getlist('folders')
            try:
                for x in folders:
                    exists = db.session.query(Folder_promo.id).filter_by(promo_id=int(promo_id), folder_type_id=int(x)).scalar() is not None
                    if exists:
                        flash("cet dossier est deja attribué à cette promo", "warning")
                        return redirect(url_for('admin_promo_card', promo_id=promo_id))
                    folders_added = Folder_promo(promo_id=int(promo_id), folder_type_id=int(x))
                    db.session.add(folders_added)
                    db.session.commit()
                flash("Le dossier a bien été ajouté à la liste des dossiers de la promo", "info")
                return redirect(url_for('admin_promo_card', promo_id=promo_id))
            except Exception as e:
                flash(str(e), "warning")

    return render_template('admin_promo_card.html', all_students=all_students, all_folders=all_folders, promo=promo, all_folders_promo=all_folders_promo)



@app.route('/admin/folders', methods=["GET", "POST"])
@login_required
@roles_required('admin')
def admin_folder():
    all_documents = Document_type.query.all()
    all_folders = Folder_type.query.all()

    if request.method == 'POST':
        
        if 'folder' in request.form:
            name_folder = request.form.get('folder')
            try:
                clean_name_folder = name_folder.replace(" ", "_").upper()
                exists = db.session.query(Folder_type.id).filter_by(name=clean_name_folder).scalar() is not None
                if exists:
                    flash("Cet dossier existe deja", "warning")
                    return redirect(url_for('admin_folder'))
                else:
                    folder = Folder_type(name = clean_name_folder)
                    db.session.add(folder)
                    db.session.commit()
                    return redirect(url_for('admin_folder'))
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_folder'))

        if 'document' in request.form:
            name_document = request.form.get('document')
            description_document = request.form.get('description')
            try:
                clean_name_document = name_document.replace(" ", "_").upper()
                exists = db.session.query(Document_type.id).filter_by(name=clean_name_document).scalar() is not None
                if exists:
                    flash("Cet dossier existe deja", "warning")
                    return redirect(url_for('admin_folder'))
                else:
                    document_type = Document_type(
                        name = clean_name_document,
                        description = description_document
                    )
                    db.session.add(document_type)
                    db.session.commit()
                    return redirect(url_for('admin_folder'))
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_folder'))

    return render_template('admin_folder.html', all_folders = all_folders, all_documents=all_documents)


@app.route('/admin/folders/<folder_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_folder_card(folder_id):
    all_documents = Document_type.query.all()
    folder_id = folder_id
    name_folder = Folder_type.query.filter_by(id=folder_id).first_or_404()
    all_documents_folder = Document_folder.query.filter_by(folder_type_id=folder_id)
    if request.method == 'POST':

        if 'documents' in request.form:
            docs = request.form.getlist('documents')
            try:
                for x in docs:
                    exists = db.session.query(Document_folder.id).filter_by(folder_type_id=folder_id, document_type_id=int(x)).scalar() is not None
                    if exists:
                        flash("Ce document fait déja parti de la liste des documents demandés", "warning")
                        return redirect(url_for('admin_folder_card', folder_id=folder_id))
                    else:
                        docs_added = Document_folder(folder_type_id=folder_id, document_type_id=int(x))
                        db.session.add(docs_added)
                        db.session.commit()
                flash("Le document a bien été ajouté à la liste des documents demandés", "info") 
                return redirect(url_for('admin_folder_card', folder_id=folder_id))
            except Exception as e:
                flash(str(e), "warning")
                return redirect(url_for('admin_folder_card', folder_id=folder_id))

    return render_template('admin_folder_card.html', name_folder=name_folder, all_documents=all_documents, all_documents_folder=all_documents_folder)


if __name__ == '__main__':
    app.run()
