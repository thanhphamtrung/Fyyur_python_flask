import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


class DatabaseURI:

    # Just change the names of your database and crendtials and all to connect to your local system
    DATABASE_NAME = "postgresql"
    username = 'postgres'
    password = 'postgres'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
