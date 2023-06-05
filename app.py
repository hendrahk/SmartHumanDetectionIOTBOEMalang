from flask import Flask, request, flash, session, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from gpiozero import DistanceSensor
ultrasonicAtas= DistanceSensor (echo=17, trigger=4)
ultrasonicKanan= DistanceSensor (echo=14, trigger=15)
ultrasonicKiri= DistanceSensor (echo=27, trigger=23)
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(100), primary_key=True, unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    db.create_all()

def bacaSonicAtas():
    nilaiTinggi = ultrasonicAtas.distance * 100
    jarakTerukur = 195.0 - nilaiTinggi
    tinggiReal = format(nilaiTinggi,".2f")
    
    return tinggiReal
    
def bacaSonicKanan():
    nilaiAwalKanan = ultrasonicKanan.distance * 100
    jarakTerukur = 100.0 - nilaiAwalKanan
    kananReal = format(jarakTerukur,".2f")
    kananf = float(kananReal)
    return kananf

def bacaSonicKiri():
    nilaiAwalKiri = ultrasonicKiri.distance * 100
    jarakTerukur = 100.0 - nilaiAwalKiri
    kiriReal = format(jarakTerukur,".2f")
    kirif = float(kiriReal)
    return kirif

def bacaLebarBadan():
    kanan = bacaSonicKanan()
    kiri = bacaSonicKiri()
    lebarBadan = 80.0 -(kanan+kiri)
    return lebarBadan

def bacaRFID():
    reader = SimpleMFRC522()
    try:
        id, text = reader.read()
        print("ID = ", id)
    finally:
        rfidRead = id
        return rfidRead

def hitungBmi(lebar):
    
    status = ""
    
    if lebar <= 44.9:
        status = 'kurus'
    elif lebar >= 45 and lebar <= 57.4:
        status = 'normal'
    elif lebar >= 57.5 and lebar <= 62.5:
        status = 'gendut'
    else:
        status = 'obesitas'
    return status


@app.route('/')
def awal():
    now = datetime.datetime.now()
    timeString = now.strftime("%d-%m-%Y")
    
    templateData = {
        'tanggal' :	 timeString,
        }
    
    return render_template('indexv1.html', **templateData)
 
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerProses', methods=['POST'])
def proses_register():
    id = request.form.get('id')
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    aidi = User.query.filter_by(id=id).first() 

    if aidi: 
        flash('id Sudah ada')
        return redirect(url_for('register'))

    new_user = User(id=id, email=email, name=name, password=password)

    
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('awal'))

@app.route('/loginProses', methods=['POST'])
def proses_login():
    user = request.form.get('user')
    password = request.form.get('password')

    user = User.query.filter_by(name=user).first()

    if (user.password != password):
        flash('cek password anda.')
        return redirect(url_for('login')) 
    
    session['username'] = user.name
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/scanrfid')
def scanRfid():
    rfid = bacaRFID()
    user = User.query.filter_by(id=rfid).first()
    
    if user == None:
        flash('anda belum terdaftar silahkan daftar disini')
        return redirect(url_for('register'))
    else:
        now = datetime.datetime.now()
        timeString = now.strftime("%d-%m-%Y")
        nama = user.name
        tinggiBadan = bacaSonicAtas()
        lebarBadan = bacaLebarBadan()
        lebarF = format(lebarBadan,".2f")
        bmi = hitungBmi(lebarBadan)
        
        templateData = {
            'tinggi' : tinggiBadan,
            'lebar' : lebarF,
            'suhu' : 33,
            'berat' : 67,
            'nama' : nama,
            'tanggal' : timeString,
            'bmi' : bmi,
            'lebar' : lebarBadan
            }
        
        return render_template('monitor.html', **templateData)

@app.route('/scanRegister')
def scanRegister():
    rfid = bacaRFID()
    templateData = {
        'rfid' : rfid
        }
    return render_template('register.html', **templateData)

@app.route('/scantanparfid')
def scanTanpRFID():
    now = datetime.datetime.now()
    timeString = now.strftime("%d-%m-%Y")
    nama = "Tamu"
    tinggiBadan = bacaSonicAtas()
    lebarBadan = bacaLebarBadan()
    lebarF = format(lebarBadan,".2f")
    bmi = hitungBmi(lebarBadan)
        
    templateData = {	
        'tinggi' : tinggiBadan,
        'lebar' : lebarF,
        'suhu' : 33,
        'berat' : 67,
        'nama' : nama,
        'tanggal' : timeString,
        'bmi' : bmi
                    }
        
    return render_template('monitor.html', **templateData)

@app.route('/demo')
def demo():
    now = datetime.datetime.now()
    timeString = now.strftime("%d-%m-%Y")
    nama = "Tamu"
    bmi = hitungBmi(60)
        
    templateData = {	
        'tinggi' : 171,
        'lebar' : 50,
        'suhu' : 35,
        'berat' : 67,
        'nama' : nama,
        'tanggal' : timeString,
        'bmi' : bmi
                    }
        
    return render_template('monitor.html', **templateData)

    
if __name__ == "__main__":
    app.run(port=5002)