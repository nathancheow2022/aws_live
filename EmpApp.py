from crypt import methods
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('registration.html') #default page

@app.route("/submit", methods=['GET', 'POST'])
def submit():
    return render_template('registration.html')

@app.route("/searchEmpButton", methods=['GET', 'POST'])
def searchEmpButton():
    return render_template('search.html')

@app.route("/searchEmp", methods=['GET','POST'])
def searchEmp():
    emp_id = request.form.get('emp_id')
    cursor = db_conn.cursor()

    query2 = "SELECT first_name FROM employee WHERE emp_id = '{}'".format(emp_id)
    cursor.execute(query2)
    first_name = cursor.fetchone()
    first_name = ''.join(first_name)

    query3 = "SELECT last_name FROM employee WHERE emp_id = '{}'".format(emp_id)
    cursor.execute(query3)
    last_name = cursor.fetchone()
    last_name = ''.join(last_name)

    query4 = "SELECT pri_skill FROM employee WHERE emp_id = '{}'".format(emp_id)
    cursor.execute(query4)
    pri_skill = cursor.fetchone()
    pri_skill = ''.join(pri_skill)

    query5 = "SELECT location FROM employee WHERE emp_id = '{}'".format(emp_id)
    cursor.execute(query5)
    location = cursor.fetchone()
    location = ''.join(location)


    query6 = "SELECT salary FROM employee WHERE emp_id = '{}'".format(emp_id)
    cursor.execute(query6)
    salary = cursor.fetchone()
    salary = ''.join(salary)


    return render_template('EdtandDeleteEmp.html',emp_id = emp_id,first_name=first_name,last_name = last_name,pri_skill = pri_skill,
                           location = location, salary = salary)

@app.route("/backMain", methods=['POST'])
def backMain():

    return render_template('registration.html')


@app.route("/updateEmp", methods=['POST'])
def updateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s,%s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location,salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        
        try:   
             print("Data inserted in MySQL RDS... uploading image to S3...")
             s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
             s3_location = (bucket_location['LocationConstraint'])

             if s3_location is None:
                s3_location = ''
             else:
                s3_location = '-' + s3_location

             object_url = "https://s3/%7B0%7D.amazonaws.com/%7B1%7D/%7B2%7D%22.format"
             s3_location,
             custombucket,
             emp_image_file_name_in_s3

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('registration.html')


        if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80, debug=True)
