#!/usr/bin/env python3

import json

from flask import (
    abort,
    Blueprint,
    jsonify,
    render_template,
    Response
)
from jinja2 import TemplateNotFound


from server.api.api import Api
from server.funcs import json
from server.games.context import GameContext


# Create game context object to use server capabilities
BOOM_GAME = GameContext(__name__)

# Create game and api blueprint - these are automatically registered on startup
bp = Blueprint(
    "boom",
    __name__,
    url_prefix="/boom",
    template_folder="../templates",
    static_folder="../static"
)
api_routes = [
    "boom/action",
    "boom/board",
    "boom/drought",
    "boom/hall"
]
api = Api(
   *api_routes,
    name="boom-api",
    path=f"{__package__}.api",
    origin="boom",
    version=BOOM_GAME.config.version
)


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

