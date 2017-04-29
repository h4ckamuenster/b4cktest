import sched
import numpy as np
import pandas as pd
import urllib.request

from datetime import datetime


URL = 'http://zeiselmair.de/h4ckamuenster/results.txt'

def download():
    try:
        ## saves the data as raw time series
        urllib.request.urlretrieve(URL, 'raw_series.txt')
        print('last download at: ' + str(datetime.now()))

        # series array
        series_array = np.loadtxt('raw_series.txt')

        series_array = series_array.transpose()

        series_df = pd.DataFrame(series_array, columns=['Time stamp', 'Adj Close'])
        series_df = series_df.set_index(['Time stamp'])
        pd.DataFrame.to_csv(series_df, 'ETH_Series.csv')

    except KeyboardInterrupt:
        print('Abgebrochen')
    threading.Timer(60, download).start()




## new = pd.read_csv('Series.csv',index_col=0)

import numpy as np
import pandas as pd
import urllib.request
from datetime import datetime
import threading
import time


class stream_series(threading.Thread):
    def __init__(self, URL, timeInterval=10):
        threading.Thread.__init__(self)
        self.iterations = 0
        self.daemon = True  # OK for main to exit even if instance is still running
        self.paused = True  # start out paused
        self.state = threading.Condition()
        self.URL = URL
        self.timeInteval = timeInterval

    def __txtload(self):
        ## saves the data as raw time series
        urllib.request.urlretrieve(self.URL, 'raw_series.txt')

        # series array
        series_array = np.loadtxt('raw_series.txt')
        series_array = series_array.transpose()
        series_df = pd.DataFrame(series_array, columns=['Time stamp', 'Adj Close'])
        series_df = series_df.set_index(['Time stamp'])
        # In this case its hard coded as ETH --> sollte noch geändert werden
        pd.DataFrame.to_csv(series_df, 'ETH_Series.csv')

    def run(self):
        self.resume() # unpause self
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            self.__txtload()
            print('last download at: ' + str(datetime.now()))
            time.sleep(self.timeInteval)
            self.iterations += 1

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # unblock self if waiting

    def pause(self):
        with self.state:
            self.paused = True  # make self block and wait
        print('Stream is currently paused!')



# kleines Beispiel zum Streamen

from stream_series import stream_series

URL = 'http://zeiselmair.de/h4ckamuenster/results.txt'

ETH_stream = stream_series(URL,20)

ETH_stream.start()

<<<<<<< HEAD
# zum Pausieren:
#ETH_stream.pause()
=======
# zum Pausieren:
#ETH_stream.pause()
>>>>>>> d071a03d5200119df21fb47c39a68e8986033f1c