"""
Defines the routes to pages for the mountain fear finder application
"""

import os
from pathlib import Path
from flask import render_template
from werkzeug.utils import secure_filename
from app import app
from app.forms import UploadForm
from get_folium_route_map import get_folium_route_map
from administer_route_database import get_loaded_routes, get_route_db_connection


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """
    Defines the home page functionality for the application
    :return: flask render_template
    """
    form = UploadForm()
    form.route_choice.choices = get_loaded_routes(get_route_db_connection())
    if form.validate_on_submit():
        route_file = form.route_file.data
        fear_level = form.fear_level.data
        route_choice = form.route_choice.data
        if route_file:
            filename = secure_filename(route_file.filename)
            route_file.save(os.path.join(
                app.instance_path, 'uploaded_files', filename
            ))
            filename = os.path.join(
                app.instance_path, 'uploaded_files', filename
            )
            route_title = Path(filename).name.replace('.gpx', '').upper()
            route_choice = None
        else:
            route_title = form.route_choice.data.upper()
            filename = None
        route_map = get_folium_route_map(fear_level, route_file=filename, route_choice=route_choice)
        form.route_choice.choices = get_loaded_routes(get_route_db_connection())
        return render_template(
            'home.html', title=f'Mountain Fear Finder - {route_title}',
            route_map=route_map, form=form, route_name=route_title)
    return render_template('home.html', title='Mountain Fear Finder',
                           form=form)
