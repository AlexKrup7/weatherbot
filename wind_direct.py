dict_wind = {
    'north': '⬆',
    'northeast': '↗',
    'northwest': '↖',
    'west': '⬅',
    'east': '➡',
    'south': '⬇',
    'southeast': '↘',
    'southwest': '↙',
}


def wind(wind_direction):
    wd_favour = ''
    if 20 > wind_direction >= 0 or 360 >= wind_direction >= 340:
        wd_favour = dict_wind['north']
    elif 67 > wind_direction >= 20:
        wd_favour = dict_wind['northeast']
    elif 112 > wind_direction >= 67:
        wd_favour = dict_wind['east']
    elif 157 > wind_direction >= 112:
        wd_favour = dict_wind['southeast']
    elif 202 > wind_direction >= 157:
        wd_favour = dict_wind['south']
    elif 247 > wind_direction >= 202:
        wd_favour = dict_wind['southwest']
    elif 292 > wind_direction >= 247:
        wd_favour = dict_wind['west']
    elif 340 > wind_direction >= 292:
        wd_favour = dict_wind['northwest']
    return wd_favour
