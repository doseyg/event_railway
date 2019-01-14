Structured flow for LogStash processing

10	INPUT		accept input and add tag for source
20	PARSE		split and convert any field data types
30	NORMALIZE	rename fields
40	ENRICH		add data such as GEOIP, Whois, usernames, 
50	TAG			add any other tags to the data
60	ROUTE		assign outputs to sendto_ tags
70	OUTPUT		output based on sendto_ tags

