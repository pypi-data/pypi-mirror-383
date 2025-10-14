import os
import importlib
from flask import Blueprint, jsonify, request, abort, g
from functools import wraps
import io

from ..utils.utils import *
import uuid
from ..utils.database import SQL_request
from ..utils import logger
from ..middleware import setup_middleware, key_role, refresh_api_keys, generate_jwt_token, decode_jwt_token
from ..config import *

api = Blueprint('api', __name__)

@api.route('/FAS', methods=['GET'])
def example():
    return jsonify({"message": "API Работает"}), 200

if config.PREFIX_KEY_ROLES:
    from .key_roles import *
if config.PREFIX_KEYS:
    from .keys import *