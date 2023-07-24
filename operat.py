from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import flask
import yaml
import uuid
import csv

app = Flask(__name__)

db = yaml.full_load(open('kers.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


######################################PARCELE###############################################################################
class Parcele():
    def __init__(self, id_parcele, br_parcele, pbr_parcele, kultura, klasa, pov, plan, skica, broj_pl, id_pl):
        self.id_parcele = id_parcele
        self.br_parcele = br_parcele
        self.pbr_parcele = pbr_parcele
        self.kultura = kultura
        self.klasa = klasa
        self.pov = pov
        self.plan = plan
        self.skica = skica
        self.broj_pl = broj_pl
        self.id_pl = id_pl

def dodaj_parcelu(parcela):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        pretraga_parcele = cur.execute("SELECT * FROM PARCELE WHERE br_parcele = %s AND pbr_parcele = %s", [parcela.br_parcele, parcela.pbr_parcele])
        if cur.fetchone() is None:
            unos = "INSERT INTO PARCELE (idPARCELE, br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, broj_pl, POS_LIST_id_pl) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            parametri = (parcela.id_parcele, parcela.br_parcele, parcela.pbr_parcele, parcela.kultura, parcela.klasa, parcela.pov, parcela.plan, parcela.skica, parcela.broj_pl, parcela.id_pl)
            cur.execute(unos,parametri)
            mysql.connection.commit()
            cur.close()
            flask.flash('Uspjesan unos!', 'succes')
        else:
            flask.flash('Parcela vec postoji!', 'danger')
            redirect(url_for('dodaj_parcele')) 
    return render_template('dodaj_parcele.html')  
        
def azuriraj_parcelu(br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, br_parcele1, pbr_parcele1):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        azuriraj = cur.execute("UPDATE PARCELE SET br_parcele = %s, pbr_parcele = %s, kultura = %s, klasa = %s, povrsina = %s, plan = %s, skica = %s WHERE br_parcele = %s AND pbr_parcele = %s ")
        parametri = (br_parcele, pbr_parcele, kultura, klasa, povrsina, plan, skica, br_parcele1, pbr_parcele1)
        cur.execute(azuriraj, parametri)
        mysql.connection.commit()
        cur.close()
        flask.flash('Uspješno ažurirani podaci!', 'succes')
    return render_template('azuriraj_parcele.html')

def izbrisi_parcelu(br_parcele, pbr_parcele):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        izbrisi = "DELETE FROM PARCELE WHERE br_parcele = %s AND pbr_parcele =%s"
        parametri = (br_parcele, pbr_parcele)
        cur.execute(izbrisi, parametri)
        mysql.connection.commit()
        cur.close()
        flask.flash('Podaci izbrisani!', 'success')
    return render_template('izbrisi_parcele.html')



    
######################################POSJEDOVNI LIST###############################################################################
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
                flask.flash('Uspjesan unos PL/LN!', 'success')
                redirect(url_for('dodaj_posjednika'))
                render_template('dodaj_posjednika.html') 
            else:
                 flask.flash('Unos mora biti broj!', 'danger')
                 redirect(url_for('dodaj_pl'))  
        else:
            flask.flash('PL/LN vec postoji!', 'danger')
            redirect(url_for('dodaj_pl'))   
    else:
        render_template('dodaj_pl.html')

######################################POSJEDNICI###############################################################################
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


def azuriraj_posjednika(ime, prezime, vrsta_prava, obim_prava, jmbg):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        azuriraj = "UPDATE POSJEDNIK SET ime = %s, prezime = %s, vrsta_prava = %s, obim_prava = %s WHERE jmbg = %s"
        parametri = (ime, prezime, vrsta_prava, obim_prava, jmbg)
        cur.execute (azuriraj, parametri)
        mysql.connection.commit()
        cur.close()
        flask.flash('Uspjesan unos!', 'succes')
    else:
        render_template('azuriraj_posjednika.html')
        
def izbrisi_posjednika(jmbg):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        izbrisi = "DELETE FROM POSJEDNIK WHERE jmbg = %s" 
        parametri = (jmbg,)
        cur.execute(izbrisi, parametri)
        mysql.connection.commit()
        cur.close()
        flask.flash('Posjednik izbrisan!', 'succes')
    else:
        render_template('izbrisi_posjednika.html')



 ######################################OSTALO###############################################################################   

def br_id_pl(broj_pl):
    cur= mysql.connection.cursor()
    preuzmi_id_pl = cur.execute("SELECT id_pl FROM POS_LIST WHERE broj_pl = %s", [broj_pl])
    rezultat = cur.fetchall()
    return rezultat

def br_pl_id_pl(id_pl):
    cur = mysql.connection.cursor()
    preuzmi_pl = cur.execute("SELECT broj_pl FROM POS_LIST WHERE id_pl = %s", [id_pl])
    rezultat = cur.fetchall()
    return rezultat      

def export_parcela():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        parcele = cur.execute("SELECT * FROM PARCELE")
        with open('parcele.csv', 'w', newline='') as parcele:
            csv_parcele = csv.writer(parcele)
            csv_parcele.writerow([i[0] for i in cur.description])
            csv_parcele.writerows(cur)
        flask.flash('Uspješan izvoz parcela!', 'succes')
    else:
        return render_template('kat_operat.html')

def export_posjednika():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        posjednici = cur.execute("SELECT * FROM POSJEDNIK")
        with open('posjednici.csv', 'w', newline='') as posjednici:
            csv_posjednici = csv.writer(posjednici)
            csv_posjednici.writerow([i[0] for i in cur.description])
            csv_posjednici.writerows(cur)
        flask.flash('Uspješan izvoz posjednika!', 'succes')
    else:
        return render_template('kat_operat.html')




