import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

table = pd.read_csv('Coefficients.csv', index_col=0)
length = 183
mean = []
for i in range(183):
    sum = np.zeros(9)
    counter = 0
    for ind in table.index:
        if str(i) == str(ind).replace('\'','')[1:]:
            counter+=1
            sum += np.array(table.loc[ind,:])
    if counter>0:
        sum = sum / counter
    mean.append(sum)



def plot(array, ip):
    names = array.index
    array = np.array(array)
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(array)), array, width=0.3, color='orangered')
    ax.set_xticks(np.arange(len(array)))
    ax.set_xticklabels(names)
    ax.set_ylabel('Value')
    fig.savefig(f'static/{str(ip)}_plot.png')

def results_from_table(long_name):
    results = np.zeros(9)
    for i in range(183):
        index = str('\'') + long_name[i] + str(i) + str('\'')
        if index in table.index:
            results+=table.loc[index,:]
        else:
            results+=mean[i]
    return results


