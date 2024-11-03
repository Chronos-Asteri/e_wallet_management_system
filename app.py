from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
engine  = SQLAlchemy(app).engine

app.secret_key = b'_324342938749$%&&^$%4'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    
    
class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False) # Name Of The Wallet
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Active")
    balance = db.Column(db.Integer, primary_key=False, default=0)
    bank_name = db.Column(db.String(100), default="")

    def __repr__(self):
        return '<Wallet %r>' % self.id
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
            
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
   
## Login // Logout // Register
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect('/')
    return render_template('login_page.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register_page.html', form=form)


## Management Functions
@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    id = current_user.id
    
    if id == 1:
        tasks = User.query.order_by(User.id).all()
        return render_template('admin.html', tasks=tasks)
    else:
        flash("Only the admin as access to 'Admin' page")
        tasks = Wallet.query.filter_by(user_id=current_user.id).order_by(Wallet.date_created).all()
        return redirect(url_for('index'))



@app.route('/user_details/<int:id>', methods=['POST', 'GET'])
@login_required
def user_details(id):
    
    if current_user.id == 1:
        tasks = Wallet.query.filter_by(user_id=id).order_by(Wallet.date_created).all()
        return render_template('user_details.html', tasks=tasks) 
    else:
        flash("Only the admin as access to 'Admin' page")
        return redirect(url_for('index'))
    
      

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Wallet(user_id=current_user.id, content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Wallet.query.filter_by(user_id=current_user.id).order_by(Wallet.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    task_to_delete = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    try:
        flash(task_to_delete.content +" Deleted Successfully")
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your wallet name'

    else:
        return render_template('update.html', task=task)
 
@app.route('/update_bank_name/<int:id>', methods=['GET', 'POST'])   
@login_required
def update_bank_name(id):
    task = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    if request.method == 'POST':
        task.bank_name = request.form['bank_name']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your Bank Name'

    else:
        return render_template('update.html', task=task)
 
@app.route('/load_money/<int:id>', methods=['GET', 'POST'])
@login_required   
def load_money(id):
    task = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    if request.method == 'POST' and task.status == "Active":
        task.balance = str(int(task.balance) + abs(int(request.form['balance'])))

        try:
            db.session.commit()
            flash("$ "+ str(abs(int(request.form['balance']))) +" Loaded to "+ task.content + " Successfully")
            return redirect('/')
        except:
            return 'There was an issue while loading wallet'

    else:
        flash('Cannot Complete Transaction When The Card Is Blocked')
        return render_template('update.html', task=task)
    
@app.route('/withdraw_money/<int:id>', methods=['GET', 'POST']) 
@login_required 
def withdraw_money(id):
    task = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    if request.method == 'POST' and task.status == "Active":
        
        after_wd = int(task.balance) - int(request.form['balance'])
        
        if after_wd < 0 :
            flash('Insufficients Funds')
            return render_template('update.html', task=task)
            
        else:            
            task.balance = str(int(task.balance) - abs(int(request.form['balance'])))

        try:
            db.session.commit()
            flash("$ "+ str(abs(int(request.form['balance']))) +" Withdrawn from "+ task.content + " Successfully")
            return redirect('/')
        except:
            return 'There was an issue while withdrawing from the wallet'

    else:
        flash('Cannot Complete Transaction When The Card Is Blocked')
        return render_template('update.html', task=task)
    
@app.route('/status_update/<int:id>', methods=['GET', 'POST']) 
@login_required  
def status_update(id):
    task = Wallet.query.filter_by(user_id=current_user.id, id=id).first()

    if request.method == 'POST':
        task.status = request.form['status']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your status'

    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
