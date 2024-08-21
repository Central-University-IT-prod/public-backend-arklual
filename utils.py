"""Module providing utils and tools for whole project."""

from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim, Yandex
import folium
import polyline
import aiohttp

from models import base, users, travels


def check_user_exist(telegram_id: int) -> bool:
    '''
    Returns True if user is already exist in db. Else returns False.
    '''
    with Session(base.engine) as session:
        exists = session.query(users.User.telegram_id).filter_by(telegram_id=telegram_id) \
                     .first() is not None
    return exists


def check_interest_exist(telegram_id: int, interest_title: str) -> bool:
    '''
    Returns True if interest is already exist in db. Else returns False.
    '''
    with Session(base.engine) as session:
        exists = session.query(users.Interest.user_id) \
                     .filter_by(user_id=telegram_id, title=interest_title) \
                     .first() is not None
    return exists


def check_travel_exist(title: str, telegram_id: int) -> bool:
    '''
    Returns True if travel with this title is already exist in travels of current user. 
    Else returns False.
    '''
    with Session(base.engine) as session:
        exists = session.query(travels.Travel.id) \
                     .filter_by(title=title, user_id=telegram_id) \
                     .first() is not None
    return exists


def check_if_locations_too_few(travel_id: int) -> bool:
    '''
    Returns True if amount of locations in current travel is 1 or fewer. Else returns False.
    '''
    with Session(base.engine) as session:
        to_few = len(session.query(travels.Location).filter_by(
            travel_id=travel_id).all()) <= 1
        print(len(session.query(travels.Location).filter_by(travel_id=travel_id).all()))
    return to_few


def get_country(lat: float, long: float) -> str:
    '''
    Returns name of country by its coordinates.
    '''
    location = get_address(lat, long, zoom=1)
    country = location.raw['address'].get('country')
    return country


def get_address(lat: float, long: float, zoom=18) -> dict:
    '''
    Geocodes coordinates.
    '''
    geolocator = Nominatim(user_agent="coltsobot")
    coordinates = f"{lat}, {long}"
    return geolocator.reverse(coordinates, exactly_one=True, language='ru', zoom=zoom)


def get_city(lat: float, long: float) -> str:
    '''
    Returns name of city by its coordinates.
    '''
    geolocator = Yandex(api_key='secret')
    coordinates = f"{lat}, {long}"
    return geolocator.reverse(coordinates, exactly_one=True, kind='locality').raw['name']


def generate_gm_link(nodes: list) -> str:
    '''
    Returns link to Google Maps route by list of coordinates.
    '''
    rtext = ''
    for node in nodes:
        (lat, long) = node
        rtext += f'{lat},+{long}/'
    result = f'https://www.google.com/maps/dir/{rtext}'
    return result


def generate_ym_link(nodes: list) -> str:
    '''
    Returns link to Yandex Maps route by list of coordinates.
    '''
    rtext = ''
    for i, node in enumerate(nodes):
        (lat, long) = node
        if i + 1 < len(nodes):
            rtext += f'{lat}%2C{long}~'
        else:
            rtext += f'{lat}%2C{long}'
    result = f'https://yandex.ru/maps/?mode=routes&rtext={rtext}&rtt=pd'
    return result


async def generate_osm_image(nodes: list) -> bytes:
    '''
    Returns image of Open Street Map with route by list of coordinates.
    '''
    routes = []
    max_lat, max_long = nodes[0]
    min_lat, min_long = nodes[0]

    for node in nodes:
        lat, long = node
        max_lat = max(lat, max_lat)
        max_long = max(long, max_long)
        min_lat = min(lat, min_lat)
        min_long = min(long, min_long)
    sum_x = 0
    sum_y = 0
    for node in nodes:
        y, x = node
        sum_x += x
        sum_y += y

    central_node = (sum_y / len(nodes), sum_x / len(nodes))
    path = ''
    for i, node in enumerate(nodes):
        lat, long = node
        path += f'{long},{lat}'
        if i + 1 != len(nodes):
            path += ';'
    route_url = f'http://router.project-osrm.org/route/v1/driving/{path}?alternatives=true&geometries=polyline'
    avalible_on_car = True
    async with aiohttp.ClientSession() as session:
        async with session.get(route_url) as response:
            res = await response.json()
            try:
                route = polyline.decode(res['routes'][0]['geometry'])
                routes += route
            except:
                avalible_on_car = False
    routes = [tuple(list(nodes)[0])] + list(routes) + [tuple(list(nodes[-1]))]
    m = folium.Map(location=central_node)
    if avalible_on_car:
        folium.PolyLine(
            locations=routes,
            color="#FF0000",
            weight=5,
        ).add_to(m)
    else:
        folium.PolyLine(
            locations=nodes,
            color="#FF0000",
            weight=5,
        ).add_to(m)
    for i, node in enumerate(nodes):
        folium.Marker(node, icon=folium.Icon(
            color='blue', prefix='fa', icon=str(i + 1))).add_to(m)
    m.fit_bounds([(min_lat, min_long), (max_lat, max_long)])
    img_data = m._to_png(5)
    return img_data


async def get_weather(node: tuple) -> str:
    '''
    Returns information about weather in current node.
    '''
    lat, lon = node
    api_key = 'secret'
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={
    lat}&lon={lon}&appid={api_key}&lang=ru&units=metric'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            temperature_min = round(float(data['main']['temp_min']))
            temperature_max = round(float(data['main']['temp_max']))
            temperature_feels = round(float(data['main']['feels_like']))
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            clouds = data['clouds']['all']
            description = []
            for i in data['weather']:
                description.append(
                    i['description'][0].upper() + i['description'][1:])
            return ('\n'.join(description) + f"""
Температура: от {temperature_min}℃ до {temperature_max}℃
Ощущается как {temperature_feels}℃
Влажность: {humidity}%
Ветер: {wind_speed} м/с
Облачность: {clouds}%""")


async def find_cafes(node: tuple) -> list:
    """
    Returns list of cafes by coordinates of city
    """
    lat, long = node
    url = "https://api.foursquare.com/v3/places/search"

    params = {
        "query": "cafe",
        "ll": f"{lat},{long}",
        "sort": "rating",
        "limit": 50,
        'fields': 'fsq_id,name,location,price,rating'
    }

    headers = {
        "Accept": "application/json",
        "Authorization": "secret"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
    result = []
    for place in data['results']:
        try:
            result.append({
                'title': place['name'],
                'city': place['location']['locality'],
                'address': place['location']['formatted_address']
            })
            if place.get('rating', None):
                result[-1]['rating'] = place.get('rating', None)
            if place.get('price', None):
                result[-1]['price'] = place.get('price', None)
        except:
            pass
    return result


async def find_hotels(node: tuple) -> list:
    """
    Returns list of hotels by coordinates of city
    """
    url = "https://api.foursquare.com/v3/places/search"
    lat, long = node
    params = {
        "query": "hotel",
        "ll": f"{lat},{long}",
        "sort": "rating",
        "limit": 50,
        'fields': 'fsq_id,name,location,description,rating,photos'
    }

    headers = {
        "Accept": "application/json",
        "Authorization": "secret"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
    result = []
    for place in data['results']:
        try:
            result.append({
                "title": place['name'],
                "city": place['location']['locality'],
                "address": place['location']['formatted_address'],
                "images": []
            })
            fsq_id = place['fsq_id']
            url = f"https://api.foursquare.com/v3/places/{fsq_id}/photos"
            headers = {
                "accept": "application/json",
                "Authorization": "secret"
            }
            if place.get('rating', None):
                result[-1]['rating'] = place.get('rating', None)
            for i in place.get('photos', []):
                result[-1]['images'].append(i['prefix'] +
                                            'original' + i['suffix'])
        except:
            pass
    return result
