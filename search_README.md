Purpose:

The intention with this script was to make validating different parsed fields easier.  I took the two most important fields and wrote a query to find potentially misparsed examples.  For the user field we are querying for users with characters not in the set of a to z, 0 to 9, a period or ending with a dollar sign.  For dest_ip I am querying for NOT \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} (ipv4) and for NOT common ipv6 formats.  


Usage:

Update the tokenUrl, tokenFile, searchUrl variables with your region's URLs and location you want to store your token cache   
You will also need to update the values of client_id and client_secret with your API secrets, or update the code to leverage a separate file.

To run the script simply pass it to python with the field you are interested in querying for.  Right now it supports two different fields, users and dest_ips.

python3 /path/to/script.py -f user
python3 /path/to/script.py -f dest_ip


