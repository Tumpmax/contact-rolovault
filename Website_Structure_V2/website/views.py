from operator import ne
import os
import pandas as pd
from re import template
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from wtforms.validators import Email
from website.forms import SignupForm, LoginForm, ContactForm, UpdateAccountForm
from website.models import User, Contact
from flask_login import login_user, current_user, logout_user, login_required
from website import db, bcrypt


views = Blueprint('views', __name__)

@views.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('views.home'))
    return render_template('signup.html', title='Signup', form=form)


@views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('views.home'))

        elif user is not None:
            with open('login_attempts.log', 'a') as Attempt:
                pass
            with open('blacklist.log', 'a') as BlackL:
                pass

                with open('blacklist.log', 'r+') as BlackL:
                    for BL in BlackL:
                        if form.email.data == BlackL: #This one checks if username in blacklist
                            flash("Account is locked, please contact the admin.")
                            return render_template('disabled_login.html', form=form)

                with open('login_attempts.log', 'r+') as Attempt:
                        for  line in range(3):
                            line = int(line)
                            filesize = os.path.getsize("login_attempts.log")
                            if filesize == 0:
                                if line == 0:
                                    new_line = line + 1
                                    Attempt.write(str(new_line))
                                    flash("Attempt: " + str(new_line))
                                    flash("Email or Password is incorrect")
                                    return render_template("login.html", title='Login', form=form, user=current_user)

                            new_line = Attempt.readlines()
                            with open('login_attempts.log', 'w') as Attempt:
                                for i in new_line:
                                    if i.strip("\n") != "2":
                                        new_line2 = int(i) + 1
                                        str_newline2 = str(new_line2) 
                                        Attempt.write(str_newline2)
                                        flash("Attempt: " + str_newline2)
                                        flash("Email or Password is incorrect")
                                        return render_template("login.html", title='Login', form=form, user=current_user)

                            with open('login_attempts.log', 'w') as Attempt:
                                for i in new_line:
                                    if i.strip("\n") != "3":
                                        new_line3 = int(i) + 1
                                        str_newline3 = str(new_line3) 
                                        Attempt.write(str_newline3)
                                    if int(str_newline3) == 3:
                                        flash("Attempt: " + str_newline3)
                                        flash("Account is locked. Please contact admin.")
                                        with open('blacklist.log', 'r+') as BlackL:
                                                BlackL.write(form.email.data)
                                                return render_template("disabled_login.html", title='Login', form=form, user=current_user)
                                                
    return render_template("login.html", title='Login', form=form, user=current_user)


@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.login'))

@views.route('/')
@login_required
def home():
    contact_amount = len(current_user.contacts)
    all_contacts = Contact.query.all()
    for contact in all_contacts:
        contact.datestp
        return render_template("home.html", all_contacts=all_contacts, contact=contact, contact_amount=contact_amount, user=current_user)
    return render_template("home.html", all_contacts=all_contacts, contact_amount=contact_amount, user=current_user)


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('views.home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('update_account.html', title='Account', form=form)


@views.route('/contacts', methods=['GET', 'POST'])
@login_required
def submit_contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                          phone_number=form.phone_number.data, address=form.address.data, city=form.city.data, state=form.state.data, subscriber=current_user)
        if contact:
            try:  
                print(contact)
                db.session.add(contact)
                db.session.commit()
                flash('Your new contact has been created!', 'success')
                return redirect(url_for('views.home'))
            except IntegrityError:
                db.session.rollback()
                flash('Contact already exists', 'warning')
                return redirect(url_for('views.submit_contact'))
                     
    return render_template('contacts.html', form=form, user=current_user)

@views.route('/contact/results')
@login_required
def results():
    contact_amount = len(current_user.contacts) 
    contacts = Contact.query.all()
    page = request.args.get('page', 1, type=int)
    for contact in contacts:
        contact.datestp
        pagination = contact.query.paginate(page=page, per_page=5)
        return render_template('results.html', pagination=pagination, contact=contact, contacts=contacts, contact_amount=contact_amount, user=current_user)
    return render_template('results.html', contacts=contacts, contact_amount=contact_amount, user=current_user)

@views.route('contact/<int:contact_id>/update', methods=['GET', 'POST'])
@login_required
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if contact.subscriber != current_user:
        abort(403)
    form = ContactForm()
    if form.validate_on_submit():
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.email = form.email.data
        contact.phone_number = form.phone_number.data
        contact.address = form.address.data
        contact.city = form.city.data
        contact.state = form.state.data
        db.session.commit()
        flash('Your contact has been updated!', 'success')
        return redirect(url_for('views.home', contact=contact))
    elif request.method == 'GET':
        form.first_name.data = contact.first_name
        form.last_name.data = contact.last_name 
        form.email.data = contact.email
        form.phone_number.data = contact.phone_number
        form.address.data = contact.address 
        form.city.data = contact.city 
        form.state.data = contact.state 
    return render_template('contacts.html', title='Update Post', contact=contact, contact_id=contact_id,
                           form=form, legend='Update Post')


@views.route('/contact/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contacts = Contact.query.get(contact_id)
    if contacts.subscriber != current_user:
        abort(403)
    db.session.delete(contacts)
    db.session.commit()
    flash('Your contact has been deleted!', 'success')
    return redirect(url_for('views.home', contacts=contacts, user=current_user))

    



