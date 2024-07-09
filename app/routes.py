from app import app, db
from flask import render_template, flash, redirect, url_for, request, abort, session
from app.forms import LoginForm, RegistrationForm, RepairsForm, AdminLoginForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, Repair, RepairStatus, AdminComment
from urllib.parse import urlsplit
from datetime import datetime, timezone
from sqlalchemy import select
from functools import wraps


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            User.admission_number == form.admission_number.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid admission number or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(admission_number=form.admission_number.data, email=form.email.data,
                    username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<admission_number>')
@login_required
def user(admission_number):
    user = User.query.filter_by(
        admission_number=admission_number).first_or_404()
    user_repairs = Repair.query.filter_by(user_id=user.id).all()
    return render_template('user.html', user=user, user_repairs=user_repairs)


@app.route('/repairs', methods=['GET', 'POST'])
@login_required
def repairs():
    form = RepairsForm()
    if form.validate_on_submit():
        repair = Repair(laptop_brand=form.laptop_brand.data,
                        serial_number=form.serial_number.data,
                        admission_number=form.admission_number.data,
                        description=form.description.data,
                        user_id=current_user.id,
                        submission_date=datetime.now(timezone.utc))
        db.session.add(repair)
        db.session.commit()
        flash('Your repair has been submitted')
        return redirect(url_for('index'))
    return render_template('repairs.html', form=form)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data) and admin.is_admin:
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invlaid email or password for admin login.')
    return render_template('admin_login.html', form=form)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.is_admin:
        repairs = Repair.query.all()
        repair_status = RepairStatus
        return render_template('admin_dashboard.html', repairs=repairs, repair_status=repair_status)
    else:
        abort(403)


@app.route('/update_repair_status/<int:repair_id>', methods=['POST'])
@login_required
def update_repair_status(repair_id):
    repair = Repair.query.get_or_404(repair_id)
    new_status = request.form['status']
    repair.status = RepairStatus(new_status)
    db.session.commit()
    flash('Repair status updated successfully.')
    return redirect(url_for('admin_dashboard'))


@app.route('/add_comment/<int:repair_id>', methods=['POST'])
@login_required
def add_comment(repair_id):
    repair = Repair.query.get_or_404(repair_id)

    comment_text = request.form.get('comment')
    if comment_text:
        new_comment = AdminComment(comment=comment_text, repair_id=repair.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully')
    else:
        flash('Comment cannot be empty')

    return redirect(url_for('admin_dashboard'))


@app.route('/add_charge/<int:repair_id>', methods=['POST'])
@login_required
def add_charge(repair_id):
    repair = Repair.query.get_or_404(repair_id)

    charge_amount = request.form.get('charge')

    if charge_amount:
        repair.charge = charge_amount
        db.session.commit()
        flash('Charges added successfully')
    else:
        flash('Charges cannot be empty')

    return redirect(url_for('admin_dashboard'))


@app.route('/submit_transaction_code/<int:repair_id>', methods=['POST'])
@login_required
def submit_transaction_code(repair_id):
    repair = Repair.query.get_or_404(repair_id)

    transaction_code = request.form.get('transaction_code')

    if transaction_code:
        repair.transaction_code = transaction_code
        db.session.commit()
        flash('Transaction code submitted successfully')
    else:
        flash('Transaction code cannot be empty')

    return redirect(url_for('user', admission_number=current_user.admission_number))


def check_activity(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_active = session.get('last_active')
        if last_active:
            last_active = last_active.replace(tzinfo=None)
            if (datetime.now() - last_active).total_seconds() > 420:
                logout_user()
                session.pop('last_active', None)
                flash('You have been logged out due to inactivity.')
                return redirect(url_for('login'))
        session['last_active'] = datetime.now()
        return func(*args, **kwargs)
    return wrapper


@app.before_request
@check_activity
def before_request():
    pass
