import os
from flask import Flask, redirect
import click

app = Flask(__name__, instance_relative_config=True)
click.echo(os.path.join(app.instance_path, 'amino.db'))
app.config.from_mapping(SECRET_KEY='dev',
                        DATABASE=os.path.join(app.instance_path, 'amino.db'))


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def home():
    return redirect('/Home')

import db

db.init_app(app)

import calc_and_draw

app.register_blueprint(calc_and_draw.bp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
