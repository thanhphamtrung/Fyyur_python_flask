# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import (render_template)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *

from routes.venues import venues_bp
from routes.artists import artists_bp
from routes.shows import shows_bp
from routes.errors import errors_bp

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(venues_bp)
app.register_blueprint(artists_bp)
app.register_blueprint(shows_bp)
app.register_blueprint(errors_bp)


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def index():
    return render_template('pages/home.html')


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
