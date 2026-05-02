#!/usr/bin/env python3

import json
import os

from flask import (
    abort,
    Blueprint,
    jsonify,
    render_template,
    Response
)
from jinja2 import TemplateNotFound

from imports import json

bp = Blueprint("boom", __name__, url_prefix="/boom", template_folder="templates", static_folder="static")


## Functions ##
@bp.route('/')
def boom():
    #TODO: This will be site entrypoint
    return Response("I'm bringing the boom!", mimetype="text/plain")


@bp.route('/config')
def boom_config():
    cfg_file = 'static/games/boom/install-config.json'
    config_vals = json.load_json(cfg_file)
    if not config_vals:
        return jsonify(valid=False, error="Boom config invalid"), 500

    try:
        script = render_template(
            "config",
            config_vals=config_vals
        )
    except TemplateNotFound:
        abort(404)

    return Response(script, mimetype="text/plain")

