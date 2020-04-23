# RedPitaya based digitiser server/client

Run the server:
`python3 digitiser_server.py`

Use the client:

```
from digitiser_client import atten_set, digitiser_acquire
return_val = atten_set(25.5)
chan0_data_array = digitiser_acquire(0)
chan1_data_array = digitiser_acquire(1)
```

