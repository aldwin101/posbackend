from flask import Flask

app = Flask(__name__)


import endpoints.users
import endpoints.login
import endpoints.dishes