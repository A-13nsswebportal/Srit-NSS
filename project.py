from flask import Flask, url_for, render_template
from flask import request, redirect, jsonify, flash, make_response
from flask import session as login_session
import random, string, os, requests, datetime
from flask import send_from_directory, make_response
from sqlalchemy import create_engine, inspect, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, relationship
from database_setup import Volunteer, Event, Circular,Studentreg, Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from flask_wtf import Form
from wtforms import StringField, IntegerField, PasswordField, FileField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Email
import flask_excel as excel



APP_ROUTE = os.path.dirname(os.path.abspath(__file__))

APPLICATION_NAME = "NSS"

app =  Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'super_secret_key'
engine = create_engine('sqlite:///sritnss.db', connect_args ={'check_same_thread':False}, echo = True )
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
login_manager = LoginManager(app)
excel.init_excel(app)

cloudinary.config(cloud_name='dqdtkki8q', api_key='985416815187587',
                  api_secret='FON4W3aFvF9TWjlwrlTIOvmGxq0')


os.environ["CLOUDINARY_URL"] = "cloudinary://985416815187587:FON4W3aFvF9TWjlwrlTIOvmGxq0@dqdtkki8q/"

global ex_sender
ex_sender = False

class LoginForm(Form):
    username = StringField('username',validators=[DataRequired("Please enter username.")])
    password = PasswordField('username',validators=[DataRequired("Please enter password.")])

class VoluntForm(Form):
    name = StringField('name',validators=[DataRequired("Please enter name.")])
    branch = StringField('branch',validators=[DataRequired("Please enter branch.")])
    rollno = StringField('rollno',validators=[DataRequired("Please enter rollno.")])
    mobile = StringField('mobile',validators=[DataRequired("Please enter mobile.")])
    email = StringField('email',validators=[DataRequired("Please enter email.")])
    gender = RadioField('Gender', choices=[('Male','Male'),('Female','Female')])
    year = IntegerField('Year')
    password = StringField('password',validators=[DataRequired("Please enter password.")])
    image = FileField('image')


@login_manager.user_loader
def load_user(user_id):
    return session.query(Volunteer).filter_by(id = user_id).first()

def check_vol_login():
    return 1 if current_user.is_authenticated else 0

def check_admin_login():
    try:
        login_session['admin_login']
        return 1
    except:
        return 0

@app.route('/')
@app.route('/home')
def home():   
    return render_template('index.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/aboutus')
def aboutus():  
    return render_template('about-us.html',admin_status = check_admin_login(), vol_status = check_vol_login())
    

@app.route('/aimobjective')
def aimobjective():  
    return render_template('aim-objective.html', admin_status = check_admin_login(), vol_status = check_vol_login())
@app.route('/trainingcentres')
def trainingcentres():  
    return render_template('training-centres.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/statenssofficer')
def statenssofficer():   
    return render_template('state-nss-officer.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/regularpgm')
def regularpgm():  
    return render_template('regular-pgm.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/special')
def special():  
    return render_template('special.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/nationallevel')
def nationallevel():  
    return render_template('national-level.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/statelevel')
def statelevel():  
    return render_template('state-level.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/districtlevel')
def districtlevel():  
    return render_template('district-level.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/collegelevel')
def collegelevel():  
    return render_template('college-level.html', admin_status = check_admin_login(), vol_status = check_vol_login())



@app.route('/circulars')
def circulars():
    data = session.query(Circular).order_by(desc(Circular.id)).all()
    return render_template('circulars.html', data = data, admin_status = check_admin_login(), vol_status = check_vol_login())


@app.route('/add/circular', methods=['GET','POST'])
def add_circular():
    if login_session['admin_login']:
        if request.method == 'POST':
            name = request.form['name']
            venue = request.form['venue']
            info = request.form['info']
            date = request.form['date']
            link = request.form['Link']
            hda = list(map(int,str(date).split("-")))
            date = datetime.date(hda[0],hda[1],hda[2])
            circ = Circular(name=name, venue=venue, info=info, date=date, link=link)
            session.add(circ)
            session.commit()
            return redirect('/circulars')
        return render_template('add_circular.html', admin_status = check_admin_login(), vol_status = check_vol_login())
    return redirect('/admin/login')

@app.route('/contact')
def contact():  
    return render_template('contact.html', admin_status = check_admin_login(), vol_status = check_vol_login())

@app.route('/student/reg/',methods=["GET","POST"])
def studentreg():
    form = VoluntForm()
    if request.method=='POST':
        name = request.form['name']
        branch = request.form['branch']
        rollno = request.form['rollno']
        mobileno = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        pic = request.files['image']
        gender = request.form['gender']
        year = request.form['year']
        if session.query(Studentreg).filter_by(rollno =rollno).one_or_none():
            return render_template("studentreg.html",err="RollNo already exists")
        if session.query(Studentreg).filter_by(mobileno =mobileno).one_or_none():
            return render_template("studentreg.html",err="Mobile already exists",form=form)
        if session.query(Studentreg).filter_by(email = email).one_or_none():
            return render_template("studentreg.html",err="Email already exists",form=form)
        url = upload(pic, folder = "/volunteers/", public_id = rollno)['url']  
        data=Studentreg(name=name,rollno=rollno,pasword = password, picture = url,email=email,branch=branch,mobileno=mobileno,gender=gender,year=year)
        session.add(data)
        session.commit()
        return redirect('/')
    return render_template('studentreg.html', form=form)



@app.route('/volunteer/login', methods = ['GET','POST'])
def volunteer_login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        vol = session.query(Volunteer).filter_by(email = email).one_or_none()
        if vol and vol.pasword == password:
            login_user(vol)
            login_session['vol_login'] = True
            flash("volunteer loged in succesfully")
            return redirect('/events')
        return render_template('volunteer_login.html',form = form, err = "username and password does not match")
    return render_template('volunteer_login.html', form=form)

@app.route('/events', methods=['GET','POST'])
def volunteer_home():
    form = LoginForm()
    if current_user.is_authenticated:
        try:
            event = session.query(Event).filter_by(vol_id = current_user.id).all()
        except:
            event = []
        return render_template('volunteer_home.html',events=event, admin_status=check_admin_login(), vol_status = check_vol_login())
    else:
        event = session.query(Event)
        return render_template('volunteer_home.html',events=event, admin_status=check_admin_login(), vol_status = check_vol_login())



@app.route('/volunteer/show_event_<int:event_id>')
def vol_show_Event(event_id):
    event = session.query(Event).filter_by(id = event_id).one()
    file = open(event.imgloc,"r")
    urls=[]
    for i in file:
        urls.append(i)
    file.close()
    return render_template("show_event.html", urls=urls, event=event, vol_status=check_vol_login(), admin_status=check_admin_login())

@app.route('/volunteer/add', methods=['GET','POST'])
def vol_add_image():
    form = LoginForm()
    if request.method=='POST':
        date = request.form['date']
        folder = "my_folder/"+str(date)+"/"
        a = "static//images//%s//"%(str(date))
        target = os.path.join(APP_ROUTE, a)
        if not os.path.isdir(target):
            os.mkdir(target)
        f_name = a+"url.txt"
        file = open(f_name, "a+")
        name = request.form['name']
        venue = request.form['venue']
        info = request.form['info']
        hda = list(map(int,str(date).split("-")))
        date = datetime.date(hda[0],hda[1],hda[2])
        # for i in range(int(request.form["count"])):
        for i in range(8):
            pic = request.files.get(str(i))
            if pic:
                url = upload(pic, folder = folder, public_id = str(i))['url']
                url+='\n'
                file.write(url)
        file.close()
        data = Event(name = name, venue=venue, imgloc=f_name, date=date, info=info, vol_id=current_user.id)
        session.add(data)
        session.commit()
        return redirect('/events')
    return render_template('vol_addimage.html')


@app.route('/volunteer/logout')
def volunteer_logout():
    logout_user()
    flash("You are Succesfuly Loged-out")
    return redirect(url_for('home'))


@app.route('/admin/login',methods = ['GET','POST'])
def adminstrator():
    if request.method == 'POST':
        if request.form['username'] == "Admin" and request.form['password'] == "admin@nss":
            login_session['admin_login'] = True
            flash("admin succesfully loged in")
            return redirect('/home')
        return render_template('admin_login.html',err = "username and password does not match")
    return render_template('admin_login.html')


@app.route('/admin/user_register/')
def user_registers():
    if not login_session['admin_login']:
        return render_template('admin_login.html')
    global ex_sender
    if ex_sender:
        Studentreg.__table__.drop(engine)
        session.commit()
        ex_sender=False
    try:
        registe = session.query(Studentreg).order_by(desc(Studentreg.id)).all()
        return render_template('stu_registers.html', regis = registe, admin_status = check_admin_login(), vol_statuss=check_vol_login())
    except:
        return render_template('stu_registers.html',admin_status = check_admin_login(), vol_status=check_vol_login())

@app.route('/admin/register_accept/<int:id>')
def register_accept(id):
    if not login_session['admin_login']:
        return render_template('admin_login.html')
    regist = session.query(Studentreg).filter_by(id = id).one()
    vol = Volunteer(name=regist.name, branch=regist.branch, rollno=regist.rollno, mobileno = regist.mobileno, gender = regist.gender, year = regist.year, email=regist.email, pasword = regist.pasword, picture = regist.picture)
    session.add(vol)
    session.delete(regist)
    session.commit()
    return redirect(url_for('user_registers'))

@app.route('/admin/export/')
def export_excel():
    if not login_session['admin_login']:
        return render_template('admin_login.html')
    global ex_sender
    ex_sender = True
    return excel.make_response_from_tables(session, [Studentreg], "xls",file_name=str(datetime.datetime.date))


@app.route('/coordinators')
def coordinators():
    vols = session.query(Volunteer).all()
    return render_template('co-ordinators.html',data = vols, admin_status = check_admin_login(), vol_status=check_vol_login())

@app.route('/add_volunteer', methods=["GET","POST"])
def add_volunteer():
    if login_session['admin_login']:
        form = VoluntForm()
        if request.method == "POST":
            name = request.form['name']
            branch = request.form['branch']
            rollno = request.form['rollno']
            mobile = request.form['mobile']
            email = request.form['email']
            password = request.form['password']
            pic = request.files['image']
            gender = request.form['gender']
            year = request.form['year']
            vols = session.query(Volunteer.id).all()
            if session.query(Volunteer).filter_by(email = email).one_or_none():
                return render_template("add_volunteer.html",err="email already exists", form = form)
            if session.query(Volunteer).filter_by(mobileno = mobile).one_or_none():
                return render_template("add_volunteer.html",err="mobile already exists", form = form)
            if session.query(Volunteer).filter_by(rollno = rollno).one_or_none():
                return render_template("add_volunteer.html",err="rollno already exists", form = form)  
            url = upload(pic, folder = "/volunteers/", public_id = rollno)['url']
            vol = Volunteer(name=name, branch=branch,gender = gender, year = year, rollno=rollno, mobileno = mobile, email=email, pasword = password, picture = url)
            session.add(vol)
            session.commit()
            return redirect('/coordinators')
        return render_template("add_volunteer.html", form = form)
    return render_template('admin_login.html')

@app.route('/edit/volunteer/<int:vol_id>', methods =['GET','POST'])
def edit_volunteer(vol_id):
    if login_session['admin_login']:
        form = VoluntForm()
        vol = session.query(Volunteer).filter_by(id = vol_id).one_or_none()
        if request.method == 'POST':
            name = request.form['name']
            branch = request.form['branch']
            rollno = request.form['rollno']
            mobile = request.form['mobile']
            email = request.form['email']
            password = request.form['password']
            pic = request.files.get('image')
            vols = session.query(Volunteer).all()
            if session.query(Volunteer).filter_by(email = email).one_or_none():
                return render_template("add_volunteer.html",err="email already exists", form = form)
            if session.query(Volunteer).filter_by(mobileno = mobile).one_or_none():
                return render_template("add_volunteer.html",err="mobile already exists", form = form)
            if session.query(Volunteer).filter_by(rollno = rollno).one_or_none():
                return render_template("add_volunteer.html",err="rollno already exists", form = form)
            vol.name = name
            vol.branch = branch
            vol.rollno = rollno
            vol.mobile = mobile
            vol.email = email
            vol.password = pasword
            if pic:
                url = upload(pic, folder = "/volunteers/", public_id = str(vol.id))['url']
            session.commit()
            return redirect('/coordinators')
        return render_template("edit_volunteer.html", form = form, vol = vol)
    return render_template('admin_login.html')

@app.route('/delete/volunteer/<int:vol_id>')
def delete_volunteer(vol_id):
    if login_session['admin_login']:
        cloudinary.api.delete_resources(str(vol_id), folder = "/volunteers/")
        session.delete(session.query(Volunteer).filter_by(id = vol_id).one())
        session.commit()
        return redirect('/coordinators')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    del login_session['admin_login']
    flash("admin succesfully loged out")
    return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
