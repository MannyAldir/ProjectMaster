# import dependancy
from flask import Flask, render_template

# create a Flask object using file name as argument
app = Flask(__name__) 

@app.route('/')
@app.route('/login') # decorator that creates directory path for function
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)