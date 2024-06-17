import pandas as pd
import numpy as np


class Rule:
    def __init__(self, letter, place):
        self.letter = letter
        self.place = place

    def get_letter(self):
        return self.letter

    def get_place(self):
        return self.place

    def __repr__(self):
        return str(self.letter) + str(self.place)


def csv_to_amino_list(file_name):
    amino_data_base = pd.read_csv(file_name)
    data_list = amino_data_base.values.tolist()
    first_row = amino_data_base.columns.tolist()
    data_list.insert(0, first_row)
    for i in range(len(data_list)):
        data_list[i][0] = data_list[i][0][len(data_list[i][0]) - 2:]
    for i in range(len(data_list)):
        for j in range(len(data_list[i])):
            data_list[i][j] = data_list[i][j][0]
    return data_list


def create_amino_df():
    A_data_list = csv_to_amino_list('A.csv')
    B_data_list = csv_to_amino_list('B.csv')
    C_data_list = csv_to_amino_list('C.csv')
    data_list = A_data_list + B_data_list + C_data_list
    return pd.DataFrame(data_list)


def csv_to_names_list(file_name):
    amino_data_base = pd.read_csv(file_name)
    data_list = amino_data_base.values.tolist()
    first_row = amino_data_base.columns.tolist()
    data_list.insert(0, first_row)
    for i in range(len(data_list)):
        data_list[i][0] = data_list[i][0][:len(data_list[i][0]) - 2].replace('\t', '')
    names = pd.DataFrame(data_list)[0].values.tolist()
    return names


def create_names_df():
    A_names = csv_to_names_list('A.csv')
    B_names = csv_to_names_list('B.csv')
    C_names = csv_to_names_list('C.csv')
    names_list = A_names + B_names + C_names
    names = pd.DataFrame(names_list)
    names.columns = ['name']
    return names


def create_weights_df():
    weights = pd.read_csv('Betas_June_18.csv')
    columns = ['rule']
    for column in weights.columns.tolist():
        columns.append(column.replace("'", "").replace("-", "_"))
    columns.remove('Unnamed: 0')
    weights.columns = columns
    for i in weights['rule']:
        weights = weights.replace(i, i.replace("'", ""))
    return weights


def create_rules_df():
    rules_string_list = weights_df['rule'].tolist()
    return pd.DataFrame([Rule(rule[0], rule[1:]) for rule in rules_string_list]).T


weights_df = create_weights_df()
rules_df = create_rules_df()


def get_amino_df():
    return create_amino_df()


def get_weights_df():
    return weights_df


def get_weights(method):
    return weights_df[method].tolist()


def get_methods_list():
    return weights_df.columns.tolist()[1:]


class AminoSequence:
    def __init__(self, sequence: str):
        self.amino_letters = sequence

    def get_amino_letters(self):
        return self.amino_letters

    def check_rule(self, rule: Rule):
        return self.amino_letters[int(rule.get_place()) - 1] == rule.get_letter()

    def calc_weight(self, method):
        rules = rules_df.values.tolist()[0]
        weights = get_weights(method)
        onehot = [0] * len(rules)
        for i in range(len(rules)):
            if self.check_rule(rules[i]):
                onehot[i] = 1
        result = 0
        for i in range(len(weights)):
            result += onehot[i] * weights[i]
        return result

    def __repr__(self):
        return str(self.amino_letters)


def get_histograms():
    methods_list = weights_df.columns.tolist()[1:]
    amino_sequences = []
    amino_lists = get_amino_df().values.tolist()
    for amino_letters_list in amino_lists:
        sequence = ''
        for amino_letter in amino_letters_list:
            sequence += amino_letter
        amino_sequences.append(AminoSequence(sequence))

    weights_for_method = {}
    for method in methods_list:
        weights_for_method[method] = [amino_sequence.calc_weight(method) for amino_sequence in amino_sequences]

    # c_weights_for_method_df = {}
    # for method in methods_list:
    #     c_weights_for_method_df[method] = pd.DataFrame(weights_for_method[method])

    hist_df_for_method = {}
    for method in methods_list:
        hist, bin_edges = np.histogram(weights_for_method[method], bins='auto')
        hist_df = pd.DataFrame(hist.tolist())
        hist_df.columns = ['bin_values']
        bin_edges_df = pd.DataFrame(bin_edges.tolist())
        bin_edges_df.columns = ['bin_edges']
        comb = pd.concat([hist_df, bin_edges_df], axis=1)
        hist_df_for_method[method] = comb
        print(method + ' hist calculated')

    return hist_df_for_method

# plt.figure(figsize=(15, 10))

# histogrms_dict = {}
# for method in weights_for_method:
#     histogrms_dict[method] = weights_for_method[method].hist(grid=False)
# plt.title(method)
