from flask import Flask, render_template, request
import os
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

@app.route('/')
def explore():
    path = request.args.get('path', '.')
    print(f'getting results for path: {path}')
    dir_list = os.listdir(path)
    directory_list = []
    file_list = []
    print(f'iterating through items in {path}')
    for item in dir_list:
        if os.path.isdir(item):
            directory_list.append(item)
        else:
            file_list.append(item)

    return render_template('index.html.jinja', files=file_list, directories=directory_list)

if __name__ == "__main__":
    app.run(debug=True)