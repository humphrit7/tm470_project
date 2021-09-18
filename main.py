from flask import Flask
import folium
import calculate_scary_points as csp
import read_gpx

app = Flask(__name__)

@app.route('/')
def home():
    route = get_route_with_scariness('data/Glenshielridge.gpx')
    first_point = (route['lat'].mean(), route['long'].mean())
    mappy = folium.Map(location=first_point, zoom_start=13)
    for index, row in route.iterrows():
        if row['scariness']>6:
            colour = 'red'
        else:
            colour = 'blue'
        if colour == 'red':
            folium.Marker(
                [row['lat'], row['long']], popup=f"<i>{row['name']}, {row['lat']}, {row['long']}, {row['elevation']}</i>",
                icon=folium.Icon(color=colour),
                tooltip="Click me").add_to(mappy)
        if colour == 'blue':
            folium.CircleMarker(
                [row['lat'], row['long']],
                popup=f"<i>{row['name']}, {row['lat']}, {row['long']}, {row['elevation']}</i>",
                tooltip="Click me").add_to(mappy)
    return mappy._repr_html_()


def get_route_with_scariness(route_file_path):
    route = read_gpx.read_gpx(route_file_path)
    route = read_gpx.pad_gpx_dataframe(route)
    route_bounds = read_gpx.get_route_bounds(route)
    altitudes_df = csp.get_complete_route_altitude_df(route_bounds)
    route = csp.calculate_route_scariness(route, altitudes_df)
    return route


if __name__ == '__main__':
    app.run(debug=True)