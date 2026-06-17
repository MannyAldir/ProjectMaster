# import dependancy
from flask import Flask, render_template, request

# create a Flask object using file name as argument
app = Flask(__name__) 

@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['GET','POST']) # decorator that creates directory path for function
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email,password)
    else:
        print('No POST info')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)