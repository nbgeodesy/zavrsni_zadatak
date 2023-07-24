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
                   flask.flash('Registracija uspjesna! Ulogujte se!', 'success')
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


@app.route('/kat')
def kat_operat():
    return render_template('kat_operat.html')

@app.route('/napredna')
def napredna_pretraga():
    return render_template('napredna_pretraga.html')


######################################POSJEDOVNI LIST###############################################################################
@app.route('/dodaj_pl/', methods = ['GET', 'POST'])
def dodaj_pl():      
    id_pl = int(uuid.uuid4())
    br_pl = request.form.get('brpl')
    pl = operat.PosList(id_pl, br_pl)
    dodaj_pl = operat.dodaj_pl(pl)
    return render_template('dodaj_pl.html')


@app.route('/pretrazi_pl/', methods = ['GET', 'POST'])
def pretraga_posjednik():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        pl = request.form.get('brpl')
        id_pl = operat.br_id_pl(pl)
        if pl.isdigit():
            pretrazi_parcelu = cur.execute("SELECT * FROM PARCELE WHERE broj_pl = %s", [pl])
            if pretrazi_parcelu > 0:
                preuzmi_parcelu = cur.fetchall()
                pretrazi_posjednika= cur.execute("SELECT * FROM POSJEDNIK WHERE POS_LIST_id_pl = %s", [id_pl])
                preuzmi_posjednika = cur.fetchall()
                flask.flash('Uspjesna pretraga!', 'success')
                return render_template('pretrazi_pl.html', rezultat = preuzmi_posjednika, rezultat1 = preuzmi_parcelu, pl = pl)
            else:
                flask.flash('Ne postoji PL/LN u bazi!', 'danger')
                return render_template('pretrazi_pl.html') 
        else:
            flask.flash('Unos mora biti broj!', 'danger')
            return render_template('pretrazi_pl.html')

    else:
        return render_template('pretrazi_pl.html')




######################################POSJEDNICI###############################################################################
@app.route('/dodaj_posjednika/', methods = ['GET', 'POST'])
def dodaj_posjednika():
    br_pl = request.form.get('pl')
    jmbg = request.form.get('jmbg')
    ime = request.form.get('ime')
    prezime = request.form.get('prezime')
    vrsta_prava = request.form.get('vrstaprava')
    obim_prava = request.form.get('obimprava')
    id_pl_preuzet = operat.br_id_pl(br_pl)
    posjednik = operat.Posjednici(jmbg, ime, prezime, vrsta_prava, obim_prava, id_pl_preuzet)
    dodaj_posjednika = operat.dodaj_posjednika(posjednik)
    return render_template('dodaj_posjednika.html')

@app.route('/azuriraj_posjednika/', methods = ['GET', 'POST'])
def azuriraj_posjednika():
    jmbg = request.form.get('jmbg')
    ime = request.form.get('ime')
    prezime = request.form.get('prezime')
    vrsta_prava = request.form.get('vrstaprava')
    obim_prava = request.form.get('obimprava')
    azuriraj = operat.azuriraj_posjednika(ime, prezime, vrsta_prava, obim_prava, jmbg)
    return render_template('azuriraj_posjednika.html')


@app.route('/izbrisi_posjednika/', methods = ['GET', 'POST'])
def izbrisi_posjednika():
    jmbg = request.form.get('jmbg')
    izbrisi = operat.izbrisi_posjednika(jmbg)
    return render_template('izbrisi_posjednika.html')



@app.route('/pretrazi_posjednika/', methods = ['GET', 'POST'])
def pretraga_pos():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        jmbg = request.form.get('jmbg')
        preuzmi_posjednika = cur.execute("SELECT * FROM POSJEDNIK WHERE jmbg = %s", [jmbg])
        if preuzmi_posjednika > 0:
            pretraga_posjednika = cur.fetchall()
            cur.execute("SELECT POS_LIST_id_pl from POSJEDNIK WHERE jmbg = %s", [jmbg])
            br_id = cur.fetchall()
            br_pl = operat.br_pl_id_pl(br_id)
            flask.flash('Uspjesna pretraga!', 'success')
            return render_template('pretrazi_posjednika.html', rezultat = pretraga_posjednika, br_pl = br_pl)
        else:
            flask.flash('Ne postoji JMBG u bazi!', 'danger')
            return render_template('pretrazi_posjednika.html')
    else:
        return render_template('pretrazi_posjednika.html')

@app.route('/pretrazi_pos/', methods = ['GET', 'POST'])   
def pretraga_pos1():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        ime = request.form.get('ime')
        prezime = request.form.get('prezime')
        preuzmi_posjednika = cur.execute("SELECT * FROM  POSJEDNIK WHERE ime = %s AND prezime = %s", [ime, prezime])
        if preuzmi_posjednika > 0:
            pretraga_posjednika = cur.fetchall()
            cur.execute("SELECT POS_LIST_id_pl from POSJEDNIK WHERE ime = %s AND prezime =%s", [ime, prezime])
            br_id = cur.fetchall()
            br_pl = operat.br_pl_id_pl(br_id)
            flask.flash('Uspjesna pretraga!', 'success')
            return render_template('pretrazi_posjednika.html',rezultat1 = pretraga_posjednika, br_pl = br_pl)
        else:
            flask.flash('Ne postoji korisnik u bazi!', 'danger')
            return render_template('pretrazi_posjednika.html')
    else:
        return render_template('pretrazi_posjednika.html')


######################################PARCELE###############################################################################
        
@app.route('/dodaj_parcele/', methods = ['GET', 'POST'])
def dodaj_parcele():    
    id_parcele = int(uuid.uuid4())
    br_parcele = request.form.get('brparcele')
    pbr_parcele = request.form.get('pbrparcele')
    kultura = request.form.get('kultura')
    klasa = request.form.get('klasa')
    povrsina = request.form.get('povrsina')
    plan = request.form.get('plan')
    skica = request.form.get('skica')
    broj_pl = request.form.get('brojpl')
    id_pl = operat.br_id_pl(broj_pl)
    parcela = operat.Parcele(id_parcele, br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, broj_pl, id_pl)
    dodaj_parcelu = operat.dodaj_parcelu(parcela)
    return render_template('dodaj_parcele.html')

@app.route('/azuriraj_parcele/', methods = ['GET', 'POST'])
def azuriraj_parcele():
    br_parcele = request.form.get('br_parcele')
    pbr_parcele = request.form.get('pbr_parcele')
    kultura = request.form.get('kultura')
    klasa = request.form.get('klasa')
    povrsina = request.form.get('povrsina')
    plan = request.form.get('plan')
    skica = request.form.get('skica')
    br_parcele1 = request.form.get('br_parcele1')
    pbr_parcele1 = request.form.get('pbr_parcele1')
    azuriraj = operat.azuriraj_parcelu(br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, br_parcele1, pbr_parcele1)
    return render_template('azuriraj_parcele.html')

@app.route('/izbrisi_parcele/', methods = ['GET', 'POST'])
def izbrisi_parcele():
    br_parcele = request.form.get('brparcele')
    pbr_parcele = request.form.get('pbrparcele')
    izbrisi = operat.izbrisi_parcelu(br_parcele, pbr_parcele)
    return render_template('izbrisi_parcele.html')

@app.route('/pretrazi_parcele/', methods = ['GET', 'POST'])
def pretraga():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        br_parcele = request.form.get('brparcele')
        if br_parcele.isdigit():
            preuzmi = cur.execute("SELECT * FROM PARCELE WHERE br_parcele = %s", [br_parcele])
            if preuzmi > 0:
                pretraga = cur.fetchall()
                flask.flash('Uspjesna pretraga!', 'success')
                return render_template('pretrazi_parcele.html', rezultat=pretraga)
            else:
                flask.flash('Ne postoji parcela u bazi!', 'danger')
                return render_template('pretrazi_parcele.html')
        else:
            flask.flash('Unos mora biti broj!', 'danger')
            return render_template('pretrazi_parcele.html')
    else:
        return render_template('pretrazi_parcele.html')


######################################OSTALO###############################################################################
@app.route('/eksport_parcela')
def eksport_parcela():
    eksport = operat.export_parcela()
    return render_template('kat_operat.html')

@app.route('/eksport_posjednika')
def eksport_posjednika():
    eksport = operat.export_posjednika()
    return render_template('kat_operat.html')

@app.errorhandler(404)
def invalid_route(e):
    return render_template("404.html")


        
        
        
        

        