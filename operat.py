from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import flask
import yaml
import uuid

app = Flask(__name__)

db = yaml.full_load(open('kers.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)



class Parcele():
    def __init__(self, id_parcele, br_parcele, pbr_parcele, kultura, klasa, pov, plan, skica, broj_pl):
        self.id_parcele = id_parcele
        self.br_parcele = br_parcele
        self.pbr_parcele = pbr_parcele
        self.kultura = kultura
        self.klasa = klasa
        self.pov = pov
        self.plan = plan
        self.skica = skica
        self.broj_pl = broj_pl


class PosList():
    def __init__(self, id_pl, broj_pl):
        self.id_pl = id_pl
        self.broj_pl = broj_pl
    def dodaj_pl(pl):
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * from POS_LIST WHERE broj_pl = %s ", [pl.broj_pl])
            if cur.fetchone() is None:
                unos = "INSERT INTO POS_LIST (id_pl, broj_pl) VALUES(%s, %s)"
                parametri = (pl.id_pl, pl.broj_pl)
                if pl.broj_pl.isdigit():
                    cur.execute(unos,parametri)
                    mysql.connection.commit()
                    flask.flash('Uspjesan unos PL/LN!', 'succes')
                    redirect(url_for('dodaj_posjednika'))  
                else:
                     flask.flash('Unos mora biti broj!', 'danger')
                     redirect(url_for('dodaj_pl'))  
            else:
                flask.flash('PL/LN vec postoji!', 'danger')
                redirect(url_for('dodaj_pl'))   
        else:
            render_template('dodaj_posjednika.html')

class Posjednici():
    def __init__(self, jmbg, ime, prezime, vrsta_prava, obim_prava, broj_pl):
        self.jmbg = jmbg
        self.ime = ime
        self.prezime = prezime
        self.vrsta_prava = vrsta_prava
        self.obim_prava = obim_prava
        self.broj_pl = broj_pl
    
    def dodaj_posjednika(posjednik):
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * from POSJEDNIK WHERE jmbg = %s", [posjednik.jmbg])
            if cur.fetchone() is None:
                unos = "INSERT INTO POSJEDNIK (jmbg, ime, prezime, vrsta_prava, obim_prava, POS_LIST_id_pl) VALUES(%s, %s,%s,%s,%s,%s)"
                parametri = (posjednik.jmbg, posjednik.ime, posjednik.prezime, posjednik.vrsta_prava, posjednik.obim_prava, posjednik.broj_pl)
                cur.execute(unos,parametri)
                mysql.connection.commit()
                flask.flash('Uspjesan unos posjednika!', 'succes')
            else:
                flask.flash('Posjednik vec postoji!', 'danger')
                redirect(url_for('dodaj_posjednika'))
        else:
            render_template('dodaj_posjednika.html')

def br_id_pl(broj_pl):
    cur= mysql.connection.cursor()
    cur.execute("SELECT id_pl FROM POS_LIST WHERE broj_pl = %s", [broj_pl])
    rezultat = cur.fetchone()
    return rezultat



#NAPRAVITI DA SE POSTAVLJA UPIT< KOLIKO POSJEDNIKA ZELITE UNIJETI U POSJEDOVNI LIST
            


def dodaj_parcelu(parcela):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        unos = "INSERT INTO PARCELE (idPARCELE, br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, broj_pl, POS_LIST_id_pl) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        parametri = (parcela.id_parcele, parcela.br_parcele, parcela.pbr_parcele, parcela.kultura, parcela.pov, parcela.plan, parcela.skica, parcela.broj_pl)
        cur.execute(unos,parametri)
        mysql.connection.commit()
        cur.close()
        flask.flash('Uspjesan unos!', 'succes')
        redirect(url_for('dodaj_parcele'))
    else:
        render_template('dodaj_parcele.html')  

def parcela_pl(br_pl):
    cur = mysql.connection.cursor()
    cur.execute("SELECT FROM POS_LIST id_pl AND id_ko WHERE broj_pl = ?", (br_pl))
    separator = ","
    result = separator.join(cur.fetchone())
    return result
    







