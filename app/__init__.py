from flask_restx import Api
from flask import Blueprint, url_for
import app.core.common.custom_exceptions as custom_exceptions
from .apis.v1 import api as api_v1

# Fix for flask-testing bug. See: https://github.com/jarus/flask-testing/issues/143
import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
############################


# from .main.controller.auth_controller import api as auth_ns


# from .apis.v1 import api as ns1


# api_v1 = Blueprint('api_v1', __name__, url_prefix="/api/v1")

# api = Api(api_v1,
#           title='Portuguese News Extractor API',
#           version='1.0',
#           description='A REST API that extracts news, from portuguese jornals, to JSON.',
#           )


# api.add_namespace(ns1, path='/news')


# # api.add_namespace(auth_ns)
# TODO: Implement following error
# @api.errorhandler(NoResultFound)
# def handle_no_result_exception(error):
#     '''Return a custom not found error message and 404 status code'''
#     return {'message': error.specific}, 404
