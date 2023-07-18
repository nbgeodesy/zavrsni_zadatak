from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
import flask
from flask_mysqldb import MySQL
import yaml
import uuid
import operat





app = Flask(__name__)
app.secret_key='Kers123*'
bootstrap = Bootstrap(app)

db = yaml.full_load(open('kers.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/registracija/', methods=["POST", "GET"])
def registracija():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        ime = request.form.get("Ime")
        prezime = request.form.get("Prezime")
        username = request.form.get('Username')
        email = request.form.get("Email")
        password = request.form.get("Password")
        password_confirm = request.form.get("Password_confirm")
        if password==password_confirm:
            if (cur.execute('SELECT * FROM User WHERE username = %s', [username]) == 0) and len(username) >=5:
               if cur.execute('SELECT * FROM User WHERE email=%s', [email])==0:
                   cur.execute('INSERT INTO User(firstname, lastname, username, email, password) VALUES(%s, %s, %s, %s, %s)', [ime, prezime, username, email, password])
                   mysql.connection.commit()
                   cur.close()
                   flask.flash('Registracija uspjesna! Ulogujte se!', 'succes')
                   return redirect(url_for('login'))
               else:
                   flask.flash('Email već postoji! Molimo registrujte se sa novom email adresom.', 'danger')
                   return render_template('registracija.html')
            else:
                flask.flash('Korisnicko ime mora imati najmanje 5 karaktera!', 'danger')
                return render_template('registracija.html')
        else:
            flask.flash('Unesene lozinke se ne poklapaju! Unesite ponovo.')
            return render_template('registracija.html')
    else:
        return render_template('registracija.html')



@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        username = request.form.get('Username')
        password = request.form.get('Password')
        if cur.execute('SELECT * FROM User WHERE username = %s AND password = %s', [username, password]) > 0:
            user = cur.fetchone()
            session['login'] = True
            session['username'] = user[6]
            session['firstname'] = user[4]
            session['lastname'] = user[5]
            mysql.connection.commit()
            cur.execute('UPDATE User SET active=1 WHERE username = %s', [username])
            mysql.connection.commit()     
            return redirect(url_for('index')) 
        else:
            flask.flash('Pogresno korisnicko ime ili lozinka', 'danger')
            return render_template('login.html')
    else:
         return render_template('login.html')                

@app.route('/logout/')
def logout():
    if session.get('username') is not None:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE User SET active = 0 WHERE username=%s", [session['username']] )
        mysql.connection.commit()
        session.pop('username')
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/kat_operat')
def kat_ko():
    return render_template('kat_operat.html')


@app.route('/dodaj_pl/', methods = ['GET', 'POST'])
def dodaj_pl():      
    id_pl = int(uuid.uuid4())
    br_pl = request.form.get('brpl')
    pl = operat.PosList(id_pl, br_pl)
    dodaj_pl = operat.PosList.dodaj_pl(pl)
    return render_template('dodaj_pl.html')
   

@app.route('/dodaj_posjednika/', methods = ['GET', 'POST'])
def dodaj_posjednika():
    if request.method == 'POST':
        jmbg = request.form.get('jmbg')
        ime = request.form.get('ime')
        prezime = request.form.get('prezime')
        vrsta_prava = request.form.get('vrstaprava')
        obim_prava = request.form.get('obimprava')
        pos_list =request.form.get('brpl')
        id_pl_preuzet = operat.br_id_pl(pos_list)
        posjednik = operat.Posjednici(jmbg, ime, prezime, vrsta_prava, obim_prava, id_pl_preuzet)
        dodaj_posjednika = operat.Posjednici.dodaj_posjednika(posjednik)
    return render_template('dodaj_posjednika.html')
    
        
@app.route('/dodaj_parcele/', methods = ['GET', 'POST'])
def dodaj_parcele():
    if request.method == 'POST':       
        id_parcele = uuid.uuid4().int
        id_parcele = str(id_parcele)
        br_parcele = request.form.get('brparcele')
        pbr_parcele = request.form.get('pbrparcele')
        kultura = request.form.get('kultura')
        klasa = request.form.get('klasa')
        povrsina = request.form.get('povrsina')
        plan = request.form.get('plan')
        skica = request.form.get('skica')
        broj_pl = request.form.get('brojpl')
        parcela = operat.Parcele(id_parcele, br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, broj_pl)
        dodaj_parcelu = operat.dodaj_parcelu(parcela)
    return render_template('dodaj_parcele.html')








        
        
        
        

