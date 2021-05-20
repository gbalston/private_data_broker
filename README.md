# PSI Server
An implementation of the De Christofaro and et Tsudik [1] protocol for private set intersection (PSI), extended to include a 'data broker' in between the two parties

## To Install
Choose your favourite environment or virtual environment

`pip install -r requirements.txt`

## To Run
Enter the required values into the query_data.txt and provider_data.txt files.

Run `gen_rsa.sh`, ensuring the input password matches that in the provider config.

Check the configs, and run query.py, provider.py, and broker.py. Find the intersecting elements at `http://server_addr/get_intersection`.

Alternatively, use the `start_all.sh` and `stop_all.sh` scripts. `stop_all.sh` uses pkill - use at your own risk.

[1] De Cristofaro, Emiliano, and Gene Tsudik. "Practical private set intersection protocols with linear complexity." Financial Cryptography and Data Security. Springer Berlin Heidelberg, 2010. 143-159.