# -*- coding: utf-8 -*-
from flask import Flask, url_for, render_template, request, redirect, jsonify
from flask.ext.mysql import MySQL
import hashlib
app = Flask(__name__)
mysql = MySQL()


app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cskir88'
app.config['MYSQL_DATABASE_DB'] = 'pharmacy'
mysql.init_app(app)

@app.route("/")
def hello():
    return "Hello World!"

# doctor app
    
@app.route("/doctor/add/")
def doctor_add():
    return render_template('doctor_add.html')
    
@app.route("/doctor/add/", methods=['POST'])
def doctor_check():
    username = request.form['username']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from doctor where username=%s", (username))
    user = cursor.fetchone()
    if user != None:
        return render_template('doctor_add.html', error=u"Ο Χρήστης υπάρχει ήδη")
    name = request.form['name']
    surname = request.form['surname']
    username = request.form['username']
    password = request.form['password']
    speciality = request.form['speciality']
    years_experience = request.form['years_experience']
    cursor.execute("insert into doctor(name, surname, username, password, speciality, years_of_experience) values(%s, %s, %s, %s, %s, %s)", (name, surname, username, password, speciality, years_experience))
    doctor_id=cursor.lastrowid
    conn.commit()
    return redirect(url_for('main_page', doctor_id=doctor_id))
     

@app.route("/doctor/")
def doctor_login():
    return render_template('doctor_login.html')
    
@app.route("/doctor/", methods=['POST'])
def doctor_auth():
    username = request.form['username']
    password = request.form['password']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from doctor where username=%s and password=%s", (username, password))
    user = cursor.fetchone()
    if user == None:
        return render_template('doctor_login.html', error=u"Λανθασμένο όνομα χρήστη ή/και κωδικός")
    return redirect(url_for('main_page', doctor_id=user[0]))    
        
@app.route("/doctor/<doctor_id>")
def main_page(doctor_id):
    return render_template('doctor_base_page.html', doctor_id=doctor_id, search=True)
    
@app.route("/doctor/<doctor_id>", methods=['POST'])
def search_patient(doctor_id):
    name = request.form['name']
    surname = request.form['surname']
    code = request.form['code']
    patients = []
    if name or surname or code:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select * from patient where name like \"" + name + "%\"" 
                        + "and surname like \"" + surname + "%\" and code like \"" + code + "%\"")
        patients = make_dict(cursor)
    return render_template('doctor_base_page.html', patients=patients, doctor_id=doctor_id, search=True)
    
@app.route("/doctor/<doctor_id>/patient/add/")
def add_patient(doctor_id):
    return render_template('patient_info.html', doctor_id=doctor_id, add=True)
    
@app.route("/doctor/<doctor_id>/patient/add/", methods=['POST'])
def insert_patient(doctor_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    name = request.form['name']
    surname = request.form['surname']
    code = request.form['code']
    area = request.form['area']
    street = request.form['street']
    street_number = request.form['street_number']
    birthdate = request.form['birthdate']
    phone = request.form['phone']
    resp_doctor = request.form['resp_doctor']
    cursor.execute("insert into patient(doctor_id, name, surname, code, area, street, street_number, phone, birthdate) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (resp_doctor, name, surname, code, area, street,
                                                         street_number, phone, birthdate))
    patient_id=cursor.lastrowid
    conn.commit()
    return redirect(url_for('show_patient', doctor_id=doctor_id, patient_id=patient_id))
    
@app.route("/doctor/<doctor_id>/patient/<patient_id>")
def show_patient(doctor_id, patient_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from patient where id=%s", patient_id)
    patients = make_dict(cursor)
    return render_template('patient_info.html', doctor_id=doctor_id, patient_id=patient_id, patient=patients[0])
    
@app.route("/doctor/<doctor_id>/patient/<patient_id>", methods=['POST'])
def update_patient(doctor_id, patient_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    name = request.form['name']
    surname = request.form['surname']
    code = request.form['code']
    area = request.form['area']
    street = request.form['street']
    street_number = request.form['street_number']
    birthdate = request.form['birthdate']
    phone = request.form['phone']
    resp_doctor = request.form['resp_doctor']
    cursor.execute("update patient set name=%s, surname=%s, code=%s, area=%s, street=%s, street_number=%s," 
                        + " birthdate=%s, phone=%s, doctor_id=%s where id=%s", (name, surname, code, area,   
                                    street, street_number, birthdate, phone, resp_doctor, patient_id))
    conn.commit()
    return redirect(url_for('show_patient', doctor_id=doctor_id, patient_id=patient_id))
    
@app.route("/doctor/<doctor_id>/patient/<patient_id>/sintagografisi/")
def sintagografisi_show(doctor_id, patient_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select drug.id as id, drug.name as drug_name, drug.formula as formula, pharma_company.name as company_name from drug inner join pharma_company on drug.pharma_company_id = pharma_company.id")
    drugs = make_dict(cursor)
    return render_template('sintagografisi.html', doctor_id=doctor_id, patient_id=patient_id, drugs=drugs)
    
@app.route("/doctor/<doctor_id>/patient/<patient_id>/sintagografisi/", methods=['POST'])
def sintagografisi_insert(doctor_id, patient_id):
    drug_id = request.form['drug_id']
    quantity= request.form['quantity']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("insert into sintagi(doctor_id, patient_id, drug_id, date, quantity)" 
                    + " values(%s, %s, %s, now(), %s)", (doctor_id, patient_id, drug_id, quantity))
    conn.commit()
    return redirect(url_for('sintagografisi_show', doctor_id=doctor_id, patient_id=patient_id))
    
@app.route("/doctor/<doctor_id>/sintages/")
def sintages_show(doctor_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select sintagi.id as id, date, patient.code as code, drug.name as name from sintagi join patient on sintagi.patient_id = patient.id join drug on sintagi.drug_id = drug.id")
    sintages = make_dict(cursor)
    return render_template('sintages.html', doctor_id=doctor_id, sintages=sintages)
    
@app.route("/doctor/<doctor_id>/sintages/<sintagi_id>/")
def sintagi_details(doctor_id, sintagi_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select sintagi.code as code, date, doctor.name as doctor_name, doctor.surname as doctor_surname, doctor.speciality as doctor_speciality, patient.name as patient_name, patient.surname as patient_surname, drug.name as drug_name, quantity from sintagi join patient on sintagi.patient_id = patient.id join drug on sintagi.drug_id = drug.id join doctor on sintagi.doctor_id = doctor.id where sintagi.id=%s", sintagi_id)
    sintagi = make_dict(cursor)
    return jsonify(sintagi[0])
    
@app.route("/doctor/<doctor_id>/drugs/")
def drugs_show(doctor_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select drug.id as id, drug.name as drug_name, formula, pharma_company.name as company_name from drug join pharma_company on drug.pharma_company_id = pharma_company.id")
    drugs = make_dict(cursor)
    return render_template('drugs.html', doctor_id=doctor_id, drugs=drugs)
    
# end of doctor app

# pharmacy app

@app.route("/pharmacy/add/")
def pharmacy_add():
    return render_template('pharmacy_add.html')
    
@app.route("/pharmacy/add/", methods=['POST'])
def pharmacy_check():
    username = request.form['username']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from pharmacy where username=%s", (username))
    user = cursor.fetchone()
    if user != None:
        return render_template('pharmacy_add.html', error=u"Ο Χρήστης υπάρχει ήδη")
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    area = request.form['area']
    street = request.form['street']
    street_number = request.form['street_number']
    phone = request.form['phone']
    cursor.execute("insert into pharmacy(name, username, password, area, street, street_number, phone) values(%s, %s, %s, %s, %s, %s, %s)", (name, username, password, area, street, street_number, phone))
    pharmacy_id=cursor.lastrowid
    conn.commit()
    return redirect(url_for('pharmacy_main_page', pharmacy_id=pharmacy_id))
     

@app.route("/pharmacy/")
def pharmacy_login():
    return render_template('pharmacy_login.html')
    
@app.route("/pharmacy/", methods=['POST'])
def pharmacy_auth():
    username = request.form['username']
    password = request.form['password']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select * from pharmacy where username=%s and password=%s", (username, password))
    user = cursor.fetchone()
    if user == None:
        return render_template('pharmacy_login.html', error=u"Λανθασμένο όνομα χρήστη ή/και κωδικός")
    return redirect(url_for('pharmacy_main_page', pharmacy_id=user[0]))    
    
@app.route("/pharmacy/<pharmacy_id>")
def pharmacy_main_page(pharmacy_id):
    return render_template('pharmacy_base_page.html', pharmacy_id=pharmacy_id, search=True)
    
@app.route("/pharmacy/<pharmacy_id>", methods=['POST'])
def search_sintagi(pharmacy_id):
    code = request.form['code']
    if code:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select sintagi.code as code, date, doctor.name as doctor_name, doctor.surname as doctor_surname, doctor.speciality as doctor_speciality, patient.name as patient_name, patient.surname as patient_surname, drug.name as drug_name, quantity from sintagi join patient on sintagi.patient_id = patient.id join drug on sintagi.drug_id = drug.id join doctor on sintagi.doctor_id = doctor.id where sintagi.code=%s", code)
        sintagi = make_dict(cursor)
    else:
        sintagi = None    
    return render_template('pharmacy_base_page.html', pharmacy_id=pharmacy_id, sintagi=sintagi[0], search=True)    
    
@app.route("/pharmacy/<pharmacy_id>/drugs/")
def drugs_list(pharmacy_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select drug.id as id, drug.name as drug_name, formula, pharma_company.name as company_name, price from drug join pharma_company on drug.pharma_company_id = pharma_company.id left join pharmacy_drug on pharmacy_drug.drug_id = drug.id join pharmacy where pharmacy.id=%s", pharmacy_id)
    drugs = make_dict(cursor)
    return render_template('pharmacy_drugs.html', pharmacy_id=pharmacy_id, drugs=drugs)
    
@app.route("/pharmacy/<pharmacy_id>/drugs/", methods=['POST'])
def drug_price(pharmacy_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    drug_id = request.form['drug_id']
    price = request.form['price']
    cursor.execute("insert into pharmacy_drug(pharmacy_id, drug_id, price) values(%s, %s, %s)", (pharmacy_id, drug_id, price))
    conn.commit()
    return redirect(url_for('drugs_list', pharmacy_id=pharmacy_id))

# end of pharmacy app    
                                    
    
    
def make_dict(cursor):
    array = cursor.fetchall()
    data = []
    for row in array:
        items = {}
        for (name, value) in zip(cursor.description, row):
            items[name[0]] = value
        data.append(items)
    return data  
    
    
if __name__ == "__main__":
    app.run()
