import sched, time
import numpy as np
import pandas as pd
import urllib.request

URL = 'http://zeiselmair.de/h4ckamuenster/results.txt'

## saves the data as raw time series
urllib.request.urlretrieve(URL, 'raw_series.txt')

# series array
series_array = np.loadtxt('raw_series.txt')

series_array = series_array.transpose()

series_df = pd.DataFrame(series_array, columns = ['Time stamp','Adj Close'])
series_df = series_df.set_index(['Time Stamp'])

pd.DataFrame.csv_write(series_df,'Series.csv')

## new = pd.read_csv('Series.csv',index_col=0)