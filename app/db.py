import sqlite3
from flask import current_app, g
import click
from flask.cli import with_appcontext
from MethodsHistCreator import *


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    # creates the tables in the data base:
    db = get_db()
    get_amino_df().to_sql('aminos', db, if_exists='replace', index=False)
    print('amino table entered')
    create_names_df().to_sql('names', db, if_exists='replace', index=False)
    print('names table entered')
    get_weights_df().to_sql('weights', db, if_exists='replace', index=False)
    print('weights table entered')
    hist_df_for_method = get_histograms()
    print('histograms calculated')
    for method in get_methods_list():
        hist_df_for_method[method].to_sql(method + '_hist', db, if_exists='replace', index=False)
        print(method + '_hist table entered the database')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')