from requests import get
from re import findall

def dolararg():
    r = get("https://www.dolarhoy.com/").text
    d = {}
    n = r.find("Dólar blue")
    d["Dólar Blue"] = findall('\$[0-9.]+', r[n:n+300])
    n = r.find("Dólar oficial promedio")
    d["Dólar Oficial"] = findall('\$[0-9.]+', r[n:n+300])
    n = r.find("Dólar Bolsa")
    d["Dólar Bolsa"] = findall('\$[0-9.]+', r[n:n+300])
    return d

def euroarg():
    r = get("https://www.dolarhoy.com/cotizacion-euro").text
    n = r.find('<div class="tile is-child title">Euro</div>')
    return findall('\$[0-9.]+', r[n:n+300])
