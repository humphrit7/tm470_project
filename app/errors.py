"""
Custom error handling for mountain fear finder application
"""

from flask import render_template
import pandas as pd
from app import app


@app.errorhandler(400)
def bad_request_error(_):
    """
    Deals with 400 error
    :param _: error, unused
    :return: flask rendered template
    """
    return render_template('400.html', tables=[pd.read_pickle(
        "locations_extremes.pkl").to_html(classes='Extremes')],
                           titles=['maximum and minimum latitude and longitude available']), 400
