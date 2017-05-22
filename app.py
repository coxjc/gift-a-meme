import os
from flask import Flask, render_template
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

@app.route('/')
def hello():
    return render_template('hello.html') 

if __name__ == '__main__':
    print(os.environ['APP_SETTINGS'])
    app.run()
