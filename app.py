from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__, 
    template_folder=os.path.abspath('templates'))
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
