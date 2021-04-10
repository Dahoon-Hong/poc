import flask
import graph

from flask import Flask, render_template, send_file
from jinja2 import Environment, FileSystemLoader

import os

app = Flask(__name__)
abs_path = os.path.abspath('./')
print(abs_path)

@app.route('/index')
def show_index():
    img_name = 'graph.png'
    graph.draw(img_name)

    env = Environment(loader=FileSystemLoader('./'))
    template = env.get_template('index.html')

    return render_template(template, user_image='/file/'+img_name)

@app.route('/file/<file_name>')
def files(file_name):
    print(file_name)
    return send_file(file_name, as_attachment=True)


if __name__ == '__main__':
    app.run(port=5000, debug=True)