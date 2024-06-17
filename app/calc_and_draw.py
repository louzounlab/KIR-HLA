import pickle

from flask import (
    Blueprint, render_template, request, send_from_directory
)

from MethodsHistCreator import *
from db import get_db

# This is a measure of allele which will be also the score of allele.
SCORE_FIELD = "Score for binding"

bp = Blueprint('/', __name__, url_prefix='/')

def load(path):
    with open(path, "rb") as f:
        obj = pickle.load(f)
        return obj 
    
def order_measures(measures):
    kirs = [m for m in measures if m.startswith("KIR")]
    others = [m for m in measures if not m.startswith("KIR")]
    a =  others + sorted(kirs)
    return a

all_vals = load("./pkl/vals.pkl")
threshold_vals = load("./pkl/threshold_vals.pkl")

all_percentiles = load("./pkl/percentiles.pkl")
threshold_percentiles = load("./pkl/threshold_percentile.pkl")

# These variables are for calculating the scores of unfamilier sequences.
sort_values = load("./pkl/sort_values.pkl")
measures_places = load("./pkl/measures_places.pkl")
coefs_indexes = load("./pkl/coefs_indexes.pkl")
matrix_new_coefs = load("./pkl/matrix_new_coefs.pkl")

alleles_list = all_vals.keys()
measures_order = order_measures(measures_places.keys())


# These function handle a case of unfamilier sequence:
# ----------------------------------------------------
def calculate_seq_vector(seq, coef_indexes):
    seq_vec = np.ndarray((len(coef_indexes),), dtype=np.int64)
    for i, (place, letter) in enumerate(coef_indexes):
        seq_vec[i] = 1 if seq[place] == letter else 0
    
    return seq_vec

def get_seq_result_dict(seq, coef_indexes, matrix_new_coefs):
    seq_oh = calculate_seq_vector(seq, coef_indexes)
    seq_result = np.matmul(seq_oh, matrix_new_coefs)
    seq_result_dict = {}
    for measure, m_index in measures_places.items():
        seq_result_dict[measure] = seq_result[m_index]
    return seq_result_dict

def get_percentile(sort_values_dict, scores):
    percentiles_for_this = {}
    
    for measure in scores:
        arr = sort_values_dict[measure]
        s = scores[measure]
        num = len(arr) - 1 

        for index, arr_index in enumerate(arr):
            if s < arr_index:
                percentiles_for_this[measure] = index / num
                break

        if measure not in percentiles_for_this:
            percentiles_for_this[measure] = 1    
    
    return percentiles_for_this

def find_name(cur, sequence):
    cur.execute("SELECT * FROM aminos")
    rows = cur.fetchall()
    sequences = []
    for tup in rows:
        s = ''
        for c in tup:
            s += c
        sequences.append(s)
    try:
        sequence_index = sequences.index(sequence) + 1
        cur.execute("SELECT name FROM names WHERE rowid = " + str(sequence_index))
        rows = cur.fetchall()
        sequence_name = rows[0][0]
    except:
        sequence_name = ''
    finally:
        return sequence_name


# def find_sequence(cur, placement):
#     cur.execute("SELECT * FROM aminos WHERE rowid = " + str(placement))
#     rows = cur.fetchall()
#     sequence = [i for i in rows[0]]
#     s = ''
#     for c in sequence:
#         s += c
#     return s

def only_upper_letters(s):
    return (all(c.isupper() for c in s[1:-1])) and (s[0].isupper() or s[0] == "*") and (s[-1].isupper() or s[-1] == "*")

def add_star(allele):
    arr = list(allele)
    arr.insert(1, "*")
    return ''.join(arr)

def convert_allele_name(allele: str):
    if allele.startswith("HLA-"):
        allele = allele[4:]
    if add_star(allele) in alleles_list:
        allele = add_star(allele)
    
    return allele

# def build_table(vals, threshold):
#     arr = []
#     for v, t in zip(vals, threshold):
#         if v <= 0 and t > 0:
#             arr.append(t)
#         elif v >= t:
#             arr.append(0)
#         elif v < t:
#             arr.append(t - v)
#     return arr

@bp.route('/Home', methods=('GET', 'POST'))
def new_page():
    if request.method == 'POST':
        cur = get_db().cursor()
        error = None

        allele_input = request.form.get("allele", "").strip()

        if allele_input:
            if allele_input in alleles_list:
                allele_name = allele_input
            elif convert_allele_name(allele_input) in alleles_list:
                # the same allele may have several names: 
                # A*01:01, A01:01, HLA-A*01:01
                allele_name = convert_allele_name(allele_input)
            elif convert_allele_name(find_name(cur, allele_input)) in alleles_list:
                allele_name = convert_allele_name(find_name(cur, allele_input))
            elif len(allele_input) == 183 and only_upper_letters(allele_input):
                allele_name = ""
            else:
                error = "Not a valid amino sequence or an allele name."
        else:
            error = "Empty input."

        if not error:
            if allele_name:
                allele_scores = all_vals[allele_name]
                allele_percentile = all_percentiles[allele_name]
            else:
                allele_scores = get_seq_result_dict(allele_input, coefs_indexes, matrix_new_coefs)
                allele_percentile = get_percentile(sort_values, allele_scores)

            measures = measures_order
            scores = [allele_scores[m] - threshold_vals[m] for m in measures_order]
            percentiles = [allele_percentile[m] for m in measures_order]
            
            percentile_threshold = [threshold_percentiles[measure] for measure in measures]

            # The score (aka weight) of allele is a specific field - binder non binder                       
            weight = round(allele_scores[SCORE_FIELD] - threshold_vals[SCORE_FIELD], 3)

            # r_values = regular = scores
            # n_values = normalized = percentiles

            # should use better names 
            return render_template('new.html', r_values=scores, measures=measures,
                                    n_values=percentiles, threshold_percent=percentile_threshold,
                                    hla_name=allele_name, current_weight=weight, 
                                    method='', alleles=alleles_list, active='Home')

        else:
            return render_template('new.html', active='Home', alleles=alleles_list, error=error)

    return render_template('new.html', active='Home', alleles=alleles_list)

@bp.route('/Help')
def help_page():
    return render_template('help.html', active='Help')

@bp.route('/Coefs')
def download_coefs():
    return send_from_directory("./excels", "Coefs.xlsx")

@bp.route('/OH')
def download_oh():
    return send_from_directory("./excels", "OH.xlsx")

@bp.route('/Example')
def example_page():
    return render_template('example.html', active='Example')

@bp.route('/About')
def about_page():
    return render_template('about.html', active='About')
