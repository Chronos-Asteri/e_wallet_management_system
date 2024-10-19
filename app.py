from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
engine  = SQLAlchemy(app).engine

app.secret_key = b'_324342938749$%&&^$%4'


class Wallets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False) # Name Of The Wallet
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Active")
    balance = db.Column(db.Integer, primary_key=False, default=0)
    bank_name = db.Column(db.String(100), default="")

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Wallets(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Wallets.query.order_by(Wallets.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    task_to_delete = Wallets.query.get_or_404(id)

    try:
        flash(task_to_delete.content +" Deleted Successfully")
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Wallets.query.get_or_404(id)

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
def update_bank_name(id):
    task = Wallets.query.get_or_404(id)

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
def load_money(id):
    task = Wallets.query.get_or_404(id)

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
def withdraw_money(id):
    task = Wallets.query.get_or_404(id)

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
def status_update(id):
    task = Wallets.query.get_or_404(id)

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
