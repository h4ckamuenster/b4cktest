# kleines Beispiel zum Streamen

import stream_series

URL = 'http://zeiselmair.de/h4ckamuenster/results.txt'

ETH_stream = stream_series(URL,20)

ETH_stream.start()

# zum Pausieren: 
#ETH_stream.pause()
