from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Event, User, Entry, Data
from market.forms import RegisterForm, LoginForm, CreateSC, JoinSC, Start
from market import db
from flask_login import login_user, logout_user, login_required, current_user
import uuid
import random
from datetime import date


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/enter', methods=['GET', 'POST'])
@login_required
def enter_page():
    form = JoinSC()
    event = Event.query.all()
    icodes = []
    for i in event:
        if i.started == False:
            icodes.append(str(i.id))
    print(icodes)

    if form.validate_on_submit():
        print("Join Validated")
        if current_user.can_enter == False:
            flash(f'You have already joined an event!', category='danger')
            return redirect(url_for('progress_page'))
        join_to_create = Entry(invite_code=form.invite_code.data,
                               wishlist=form.wishlist.data)
        if str(join_to_create.invite_code) not in icodes:
            flash(f'Please enter a valid invite code!', category='danger')
            return render_template('market.html', form=form)
        if str(join_to_create.owner_name) == str(current_user.username):
            return redirect(url_for('progress_page'))
        current_user.invite_code = join_to_create.invite_code
        current_user.wishlist = join_to_create.wishlist
        current_user.can_enter = False
        for i in event:
            if str(i.id) == str(current_user.invite_code):
                i.users = str(i.users) + ',' + str(current_user.username)
                join_to_create.set_owner(current_user)
        join_to_create.owner_name = current_user.username
        db.session.add(join_to_create)
        db.session.commit()
        flash(f"Successfully joined event!", category='success')
        return redirect(url_for('progress_page'))
    return render_template('market.html', form=form)


@login_required
@app.route('/progress', methods=["GET", "POST"])
def progress_page():
    entry = Entry.query.all()
    event = Event.query.all()
    form = Start()
    fData = Data().query.all()
    user = User().query.all()
    data = []

    for e in event:
        print(e.users)
        data = e.users.split(',')
        print(data)
        print('e.started is: ' + str(e.started))
        if str(current_user.invite_code) == str(e.id):
            if e.started == True:
                print('e.dataDisplayed is: ' + str(e.displayed))
                if e.displayed == False:
                    print('false called')
                    d=0
                    da=[]
                    for d in range (len(data)):
                        da.append(data[d])
                        d+=1
                    i = 0
                    print('da is' + str(da))
                    resultses = ''
                    for i in range(len(da)):
                        resultses = ' '.join(da)
                        print('resultses is ' + str(resultses))
                        i += 1
                    data_to_create = Data()
                    data_to_create.results = resultses
                    data_to_create.invite_code = current_user.invite_code
                    e.displayed=True
                    print(data_to_create.results)
                    print('e.dataDisplayed now is: ' +
                            str(e.displayed))
                    db.session.add(data_to_create)
                    db.session.commit()
                    return redirect(url_for('progress_page'))
                elif e.displayed == True:
                    print('True called!')
                    print(fData)
                    for fdat in fData:
                        print(fdat.results)
                        print("ITERATING")
                        if fdat.invite_code == current_user.invite_code:
                            print("CHECK PASSEd")
                            n=0
                            fdat.results.split(' ')
                            u = []
                            print(str(fdat.results.split(' ')) + " is m.results")
                            for result in fdat.results.split(' '):
                                if str(result) != str(None):
                                    print(str(result))
                                    u.append(result)
                            n=0
                            print(u)
                            for n in range (len(u)):
                                if u[n] == current_user.username:
                                    if n+1 < len(u):
                                        p = u[n+1]
                                    else:
                                        p=u[0]
                            for h in user:
                                if h.username == p:
                                    w = str(h.wishlist)
                            d = ''
                    return render_template('progress.html', p=p, w=w, d=d)
            elif str(current_user.id) == str(e.owner):
                print("Else Called")
                if e.started == False:
                    person = 'undetermined'
                    p = 'undetermined'
                    w = 'undetermined'
                    d = 'Press announce to display results!'
                    if form.validate_on_submit():
                        e.started = True
                        db.session.commit()
                        return redirect(url_for('progress_page'))
                    return render_template('progress copy.html', person=person, p=p, w=w, d=d, form=form)
    person = 'undetermined'
    p = 'undetermined'
    w = 'undetermined'
    d = 'Please check back later!'
    return render_template('progress.html', person=person, p=p, w=w, d=d, form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_page():
    form = CreateSC()
    if request.method == "POST":
        print("Event Created")
        print("Code is" + str(id))
        event_to_create = Event(started=False, displayed=False)
        event_to_create.set_owner(current_user)
        db.session.add(event_to_create)
        db.session.commit()
        flash(
            f'Event successfully created! {event_to_create.id} is the code', category='success')
        return redirect(url_for('enter_page'))
    return render_template("create.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.is_submitted():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(
            f'Account successfully created! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('enter_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(
            username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('enter_page'))
        else:
            flash('Username and password are not match! Please try again',
                  category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home_page'))
