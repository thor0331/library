from flask import Flask, render_template, url_for, request
import sqlite3
import csv
import os
import cv2
import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
command = """CREATE TABLE IF NOT EXISTS admin(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)
command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)
command = """CREATE TABLE IF NOT EXISTS books(book TEXT, row TEXT, column TEXT)"""
cursor.execute(command)
command = """CREATE TABLE IF NOT EXISTS records(email TEXT, book TEXT, start TEXT, end TEXT, return TEXT)"""
cursor.execute(command)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Pay')
def pay():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    f = open('session.txt', 'r')
    email = f.readline()
    f.close()

    today = date.today()
    today = pd.to_datetime(today)
    today = today.strftime('%Y-%m-%d')

    cursor.execute("UPDATE records set return = '"+today+"' where email='"+email+"'")
    connection.commit()

    img = cv2.imread('QR.png')
    cv2.imshow('payment', img)
    cv2.waitKey(10000)
    cv2.destroyAllWindows()
    return render_template('userlog.html', msg3 = "Successfully transaction completed")

@app.route('/notification')
def notification():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    query = "SELECT * FROM records"
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    status = 0
    if data:
        for row in data:
            print(row)
            if row[-1]:
                status = 1
            else:
                today = date.today()
                today = pd.to_datetime(today)
                duedate = pd.to_datetime(row[3])
                if (today - duedate).days > 0:
                    bot.sendMessage("1388858613", str(f"Dear {row[0]} due date is completed{row[3]} please return book soon with fine RS. 100"))

    return render_template('adminlog.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        email = request.form['email']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE email = '"+email+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if len(result) == 0:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
        else:
            f = open('session.txt', 'w')
            f.write(email)
            f.close()
            return render_template('userlog.html')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        email = request.form['email']
        password = request.form['password']

        query = "SELECT name, password FROM admin WHERE email = '"+email+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if len(result) == 0:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
        else:
            return render_template('adminlog.html')

    return render_template('index.html')


@app.route('/adminreg', methods=['GET', 'POST'])
def adminreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        cursor.execute("INSERT INTO admin VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/update_book', methods=['GET', 'POST'])
def update_book():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        book = request.form['book']
        # row = request.form['row']
        # column = request.form['column']
        if book == 'vlsi':
            row = 1
            column = 1
        if book == 'network':
            row = 1
            column = 2
        
        if book == 'tagr':
            row = 2
            column = 1
        if book == 'writing':
            row = 2
            column = 2

        row = str(row)
        column = str(column)
        print(book, row, column)

        cursor.execute("INSERT INTO books VALUES ('"+book+"', '"+row+"', '"+column+"')")
        connection.commit()

        if os.path.exists('requests.csv'):
            df = pd.read_csv('requests.csv')
            books = df.loc[df['book']==book]
            if not books.empty:
                print('{} book now available'.format(book))
                df.drop(df[df['book'] == book].index, inplace=True)
                df.to_csv('requests.csv', index=False)
        return render_template('adminlog.html', msg='Successfully updated')
    
    return render_template('adminlog.html')

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        book = request.form['book']
        print(book)

        from serial_test import send_data
        if book == 'vlsi':
            row = 1
            column = 1
            send_data('a')
        if book == 'network':
            row = 1
            column = 2
            send_data('b')
        
        if book == 'tagr':
            row = 2
            column = 1
            send_data('d')
        if book == 'writing':
            row = 2
            column = 2
            send_data('e')

        row = str(row)
        column = str(column)
        print(book, row, column)

        cursor.execute("INSERT INTO books VALUES ('"+book+"', '"+row+"', '"+column+"')")
        connection.commit()

        f = open('session.txt', 'r')
        email = f.readline()
        f.close()

        today = date.today()
        today = pd.to_datetime(today)
        today = today.strftime('%Y-%m-%d')

        cursor.execute("UPDATE records set return = '"+today+"' where email='"+email+"'")
        connection.commit()
        
        if os.path.exists('requests.csv'):
            df = pd.read_csv('requests.csv')
            books = df.loc[df['book']==book]
            if not books.empty:
                print('{} book now available'.format(book))
                df.drop(df[df['book'] == book].index, inplace=True)
                df.to_csv('requests.csv', index=False)
        return render_template('userlog.html', msg='Successfully updated')
    
    return render_template('userlog.html')

@app.route('/buy_book', methods=['GET', 'POST'])
def buy_book():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        book = request.form['book']
        print(book)

        query = "SELECT * FROM books WHERE book = '"+book+"'"
        cursor.execute(query)

        result = cursor.fetchone()

        if not result:
            return render_template('userlog.html', msg1="{} book not available".format(book), book=book, pdf = 'http://127.0.0.1:5000/static/books/'+book+'.pdf')
        else:
            f = open('session.txt', 'r')
            email = f.readline()
            f.close()

            query = "SELECT * FROM records WHERE email = '"+email+"'"
            cursor.execute(query)
            data = cursor.fetchall()
            print(data)
            status = 0
            if data:
                for row in data:
                    print(row)
                    if row[-1]:
                        status = 1
            
            if status == 0:
                return render_template('userlog.html', msg2="please return previous book")
            else:
                book = result[0]
                row = result[1]
                column = result[2]

                print(book, row, column)

                from serial_test import send_data
                if row == '1' and column == '1':
                    print('A')
                    send_data('A')
                if row == '1' and column == '2':
                    print('B')
                    send_data('B')

                if row == '2' and column == '1':
                    print('D')
                    send_data('D')
                if row == '2' and column == '2':
                    print('E')
                    send_data('E')


                cursor.execute("delete from books where book = '"+book+"'")
                connection.commit()

                f = open('session.txt', 'r')
                email = f.readline()
                f.close()

                today = date.today()
                today = pd.to_datetime(today)

                deadline = today + timedelta(days=10)

                today = today.strftime('%Y-%m-%d')
                deadline = deadline.strftime('%Y-%m-%d')

                cursor.execute("INSERT INTO records(email, book, start, end ) VALUES ('"+email+"', '"+book+"', '"+today+"', '"+deadline+"')")
                connection.commit()

                return render_template('userlog.html', msg="{} book available, collect it".format(book))
    
    return render_template('userlog.html')

@app.route('/request_book/<book>')
def request_book(book):
    print(book)
    if not os.path.exists('requests.csv'):
        f = open('requests.csv', 'a', newline='')
        writer = csv.writer(f)
        writer.writerow(['book'])
        f.close()

    f = open('requests.csv', 'a', newline='')
    writer = csv.writer(f)
    writer.writerow([book])
    f.close()
    return render_template('userlog.html', msg='requested for {} book'.format(book))

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
