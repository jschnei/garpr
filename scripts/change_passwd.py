import base64
import hashlib
import os
import sys

# add root directory to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from pymongo import MongoClient, DESCENDING

from config.config import Config
from model import User
from dao import USERS_COLLECTION_NAME, DATABASE_NAME, ITERATION_COUNT


# script to change users password
def change_passwd():
    if len(sys.argv) != 3:
        print "incorrect number of arguments!"
        print "usage: python change_passwd.py username password"
        return

    username = sys.argv[1]
    password = sys.argv[2]
    config = Config()
    mongo_client = MongoClient(host=config.get_mongo_url())

    # more bytes of randomness? i think 16 bytes is sufficient for a salt
    salt = base64.b64encode(os.urandom(16))

    hashed_password = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password, salt, ITERATION_COUNT))
    users_col = mongo_client[DATABASE_NAME][USERS_COLLECTION_NAME]

    # modifies the users password, or returns None if it couldnt find the user
    if not users_col.find_and_modify(query={'username': username}, update={"$set": {'hashed_password': hashed_password, 'salt': salt}}):
        print "user not found! you done goofed"
    else:
        print "password updated sucessfully"


if __name__ == "__main__":
    change_passwd()
