import base64
import hashlib
import os
import sys

# add root directory to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId

from config.config import Config
from model import User, Region
from dao import DATABASE_NAME, ITERATION_COUNT, \
                REGIONS_COLLECTION_NAME, USERS_COLLECTION_NAME


def create_user():
    if len(sys.argv) < 4:
        print "incorrect number of arguments!"
        print "usage: python create_user.py username password region1 [region2] [region3]...."
        return

    username = sys.argv[1]
    password = sys.argv[2]
    regions =  sys.argv[3:]
    config = Config()
    mongo_client = MongoClient(host=config.get_mongo_url())

    regions_col = mongo_client[DATABASE_NAME][REGIONS_COLLECTION_NAME]
    valid_regions = [Region.from_json(region).id for region in regions_col.find()]
    print valid_regions

    for region in regions:
        if region not in valid_regions:
            print 'Invalid region name:', region

    regions = [region for region in regions if region in valid_regions]
    if len(regions) == 0:
        print 'No valid region for new user'
        return

    # more bytes of randomness? i think 16 bytes is sufficient for a salt
    salt = base64.b64encode(os.urandom(16))

    hashed_password = base64.b64encode(hashlib.pbkdf2_hmac('sha256', password, salt, ITERATION_COUNT))
    the_user = User(ObjectId(), regions, username, salt, hashed_password)
    users_col = mongo_client[DATABASE_NAME][USERS_COLLECTION_NAME]

    # let's validate that no user exists currently
    if users_col.find_one({'username': username}):
        print "already a user with that username in the db, exiting"
        return

    users_col.insert(the_user.get_json_dict())


if __name__ == "__main__":
    create_user()
