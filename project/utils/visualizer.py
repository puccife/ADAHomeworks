import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_countries_situation(most_involved_leak, divide_by='Country', selected_jurisdiction=None):
    if(selected_jurisdiction != None):
        leaks = []
        for country in most_involved_leak:
            leak = country.copy()
            leak = leak.reset_index()
            leak = leak[leak['jurisdiction'] == selected_jurisdiction]
            leaks.append(leak)
    else:
        leaks = most_involved_leak
    for index_, country_result in enumerate(leaks):     
        sns.factorplot(x='date', 
                   y='offshores', 
                   row=divide_by, 
                   data=country_result, 
                   hue='action',
                   kind='bar', 
                   sharey=True, 
                   sharex=False,
                   size=4,
                   aspect=4)