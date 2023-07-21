from flask import Blueprint, render_template, jsonify

errors_bp = Blueprint('errors_bp', __name__)


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 400,
        'message': 'Bad request'
    }), 400


@errors_bp.app_errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@errors_bp.app_errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 403,
        'message': 'Forbidden'
    }), 403


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 404,
        'message': 'Not found'
    }), 404


@errors_bp.app_errorhandler(500)
def server_error(error):
    return jsonify({
        'error': 500,
        'message': 'Server error'
    }), 500


@errors_bp.app_errorhandler(422)
def not_processable(error):
    return jsonify({
        'error': 422,
        'message': 'Unprocessable entity'
    }), 422


@errors_bp.app_errorhandler(405)
def invalid_method(error):
    return jsonify({
        'error': 405,
        'message': 'Method not allowed'
    }), 405


@errors_bp.app_errorhandler(409)
def duplicate_resource(error):
    return jsonify({
        'error': 409,
        'message': 'Duplicate resource'
    }), 409
