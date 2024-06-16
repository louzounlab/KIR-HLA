import os
import pickle
import pandas as pd
import uuid
from zipfile import ZipFile
from os.path import basename
import shutil
import torch
import numpy as np
import pandas as pd
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from pathlib import Path
from datetime import datetime
import os
from get_plot import plot, results_from_table
bp = Blueprint('/', __name__, url_prefix='/')

input_dir = "static/input/"
output_dir = "static/output/"
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)


@bp.route('/Home', methods=('GET', 'POST'))
def home_page():
    error = None

    if request.method == 'POST':
        allelle_table = pd.read_csv( os.getcwd() + '/Allele.csv', index_col=0)
        name = str(request.form['short_name'])
        long_name = str(request.form['long_name'])
        ip = request.remote_addr

        if name and name in allelle_table.index:
            results = allelle_table.loc[name,:]
        elif not name and not long_name:
            error = 'please enter an allele\'s name.'
        elif name not in allelle_table.index and not long_name:
            error = f'{name} is not a valid allele.'
        elif long_name:
            if len(long_name)==183:
                results = results_from_table(long_name)
                results = pd.Series(results)
                results.index = np.arange(9)+1
            else:
                error = f'Not a valid allele. length is not 183.'

        if not error:
            try:
                plot(results, str(ip))
                name= 'static/' + str(ip) + '_plot.png'
            except:
                error = 'Error occurred while creating the results.'
        if error:
            flash(error)

        if error:
            return render_template('Home_new.html', error_message=error, results=False)
        else:
            return render_template('Home_new.html', error_message='', results=True, name=name)

    return render_template('Home_new.html', error_message="", results=False)


@bp.route('/Help')
def help_page():
    return render_template('Help.html')


@bp.route('/Example')
def example_page():
    return render_template('Example.html')


@bp.route('/About')
def about_page():
    return render_template('About.html')
