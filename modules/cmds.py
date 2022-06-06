VERSION = 'v1.3.9'
import random
#from mal import AnimeSearch
#import chistesESP as c
import requests
import json
import re
import pytz
import base64
import traceback
from datetime import datetime
from io import BytesIO
#from gtts import gTTS
from requests import get
from urllib import parse
from shlex import split
from json import load, dumps
from os import listdir, rename, remove, _exit, popen
from sys import platform
from functools import partial
from operator import is_not
from threading import Thread
from modules import caesar
from modules import binen
from modules import dolar
from time import sleep
td = load(open('modules/td.json', 'r'))

if not 'ccmd.json' in listdir("modules"):
    ccmd = open('modules/ccmd.json', 'w+')
    ccmd.write('{}')
    ccmd.close()

ccmd = load(open('modules/ccmd.json'))

def timedexec(foo, data, t):  # Not a command
    sleep(t)
    foo(data)
    return {"chatId": data.message.chatId,
            "message": ""}

def sintilde(x):  # Not a command
    eq = (
            ('á', 'a'),
            ('é', 'e'),
            ('í', 'i'),
            ('ó', 'o'),
            ('ú', 'u')
        )
    for a,b in eq:
        x = x.replace(a, b).replace(a.upper(), b.upper())
    return x

def search_users(sub, u, n="normal"):  # Not a command
    if u.startswith("https://aminoapps.com/p/"):
        u = u[24:]
        data = sub.get_from_code(u).objectId
        if n == "normal":
            return sub.get_user_info(data)
        return data
    elif u.startswith("https://aminoapps.com/u/"):
        return
    elif u.startswith("ndc://user-profile/"):
        data = u[19:]
        if n == "normal":
            return sub.get_user_info(data)
        return data
    else:
        data = sub.search_users(u)
        if n == "uid":
            if data.userId:
                return data.userId[0]
            else:
                return
        return data

def joinparams(x):  # Not a command
    s = ""
    for i in x:
        s += f"{i} "
    return s.strip()

def rut(c, d):
    return {"chatId": c.chatId,
            "message": d}

def update():  # Not a command
    f = open("modules/data.json", "w")
    f.write(dumps(TDATA, indent=4))
    f.close()

def chnick(subclient, *params):
    """
    Cambiar el nickname
    :param subclient: amino.SubClient()
    :param params: nickname, message object
    :rtype: tuple
    """
    if not params[1].author.userId in params[2]["ADMIN"]:
        print(params[1].author.nickname)
        print(params[2]["ADMIN"])
        return {"chatId": params[1].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    try:
        subclient.edit_profile(nickname=params[0][0])
        subclient.edit_profile(nickname=params[0][0])
        return {"chatId": params[1].chatId,
                "message": "Hecho!"}
    except:
        return {"chatId": params[1].chatId,
                "message": "Error al configurar el nickname"}

def chbio(subclient: object, *params):
    """
    Cambiar la biografía del perfil
    :param subclient: amino.SubClient()
    :param params: biografía, message object
    :rtype: tuple
    """
    if not params[1].author.userId in params[2]["ADMIN"]:
        return {"chatId": params[1].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    subclient.edit_profile(content=params[0][0])
    return {"chatId": params[1].chatId,
                "message": "Hecho!"}

def chprofpic(subclient: object, *params):
    """
    Cambiar la foto del perfil
    :param subclient: amino.SubClient()
    :param params: None, data.message
    :rtype: tuple
    """
    if not params[1].author.userId in params[2]["ADMIN"]:
        return {"chatId": params[1].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}

    if params[1].extensions and 'mediaValue' in params[1].extensions['replyMessage']:
        pic = params[1].extensions['replyMessage']['mediaValue']
    else:
        return {"chatId": params[1].chatId,
                "message": "Error, el mensaje solicitado no es una imagen"}
    try:
        subclient.edit_profile(icon=pic)
        subclient.edit_profile(icon=pic)
        return {"chatId": params[1].chatId,
                "message": "Hecho!"}
    except:
        return {"chatId": params[1].chatId,
                "message": "Error al configurar la imagen"}

def echo(*params):
    """
    Devuelve lo que se le pasa como argumento
    :param params: None, str, messageType=0
    :rtype: tuple
    """
    if len(params[1]) < 1:
        return {"chatId": params[2].chatId,
                "message": "Falta un argumento: <string>"}
    if len(params[1]) > 1 and params[1][1].isdigit():
        return {"chatId": params[2].chatId,
                "message": params[1][0],
                "messageType": int(params[1][1])}
    return {"chatId": params[2].chatId,
            "message": params[1][0]}


def join(subclient: object, *params):
    """
    Une el bot a un chat
    :param subclient: amino.SubClient()
    :param params: link hacia el chat
    :rtype: tuple
    """
    try:
        subclient.join_chat(subclient.get_from_code(params[0][0]).objectId)
        return {"chatId": params[1].chatId,
                "message": "Hecho!"}
    except:
        return {"chatId": params[1].chatId,
                "message": "Hubo un error en el proceso"}


def leave(subclient: object, *params):
    """
    Deja el chat desde el que se ejecute el comando
    :param subclient: amino.SubClient()
    :param params: None, data.message
    :rtype: tuple
    """
    if not params[1].author.userId in params[2]["ADMIN"]:
        print(params[1].author.nickname)
        print(params[2]["ADMIN"])
        return {"chatId": params[1].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    subclient.leave_chat(params[1].chatId)
    return {"chatId": params[1].chatId,
            "message": "Hecho!"}


def rm(subclient: object, *params):
    """
    Elimina la cantidad de mensajes que se especifiquen
    :param subclient: amino.SubClient
    :param params: numero de mensajes a eliminar, si se quiere eliminar como Staff
    :type params: int, bool
    :rtype: tuple
    """
    if params[0] and params[0][0].isdigit:
        if int(params[0][0]) > 50:
            return {"chatId": params[1].chatId,
                    "message": "No voy a borrar tantos mensajes, alta flojera"}
        msg = subclient.get_chat_messages(params[1].chatId, int(params[0][0])).messageId
        if len(params[0]) > 1 and eval(params[0][1]) and params[1].author.userId in params[2]["ADMIN"]:
            for i in msg:
                subclient.delete_message(chatId=params[1].chatId, messageId=i, asStaff=True, reason='-')
        else:
            for i in msg:
                subclient.delete_message(messageId=i, chatId=params[1].chatId)
        return {"chatId": params[1].chatId,
                "message": f"Se han eliminado {len(msg)} mensajes"}
    else:
        return {"chatId": params[1].chatId,
                "message": "Se ha producido un error en la operación"}


def choice(*params):
    """
    Escoge entre una lista de cosas
    :param params: None, lista separada por comas
    :rtype: tuple
    """
    li = [i.strip() for i in params[1][0].split(',')]
    li = list(filter(partial(is_not, None), li))
    return {"chatId": params[2].chatId,
            "message": random.choices(li)[0]}


def rand(*params):
    """
    Devuelve un número aleatorio entre dos números dados
    :param params: None, dos números separados por comas
    :rtype: tuple
    """
    try:
        li = [int(i.strip()) for i in params[1][0].split(',')]
    except ValueError:
        return {"chatId": params[2].chatId,
                "message": "Uno de los valores especificados no es un número"}
    li = list(filter(None, li))
    if len(li) == 2:
        return {"chatId": params[2].chatId,
                "message": str(random.randint(li[0], li[1]))}
    else:
        return {"chatId": params[2].chatId,
                "message": "La lista presenta más o menos de 2 números"}


def truth(*params):
    return {"chatId": params[2].chatId,
            "message": random.choices(td['Truth'])[0]['summary']}


def dare(*params):
    return {"chatId": params[2].chatId,
            "message": random.choices(td['Dare'])[0]['summary']}


def newton(*params):
    params[1][0] = params[1][0].replace('**', '^')
    if '^' in params[1][0]: return {"chatId": params[2].chatId,
            "message": "La potenciación fue bloqueada temporalmente"}
    return {"chatId": params[2].chatId,
            "message": get(f'https://newton.now.sh/api/v2/simplify/{parse.quote(params[1][0])}').json()['result']}

def ping(*params):
    return {"chatId": params[2].chatId,
            "message": "pong"}

def hlp(*params):
    return {"chatId": params[2].chatId,
            "message": """[C]橱         𝐖𝐄𝐋𝐂𝐎𝐌𝐄     
[C]
[C]¡Hola Hola! ヾ(o˃‿˂o)ｼᵎ
[C]Soy funkeyroll, tú pequeño bot que te hará este chat mucho más divertido y ameno,para eso tienes mi guía de comandos, la cual están dividas en las  siguientes categorías: 
[C]dueño, entretenimiento, acciones, ayudante, comunes
[C]
[C]Ejemplo: /dueño
[C]
[C]Mi creador? coloca /creador 
[C]Quieres oportar una sugerencia? usa esto:
[C]Ejemplo: 
[C]/sugerencia add "ejemplo" 
[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}


def info(*params):
    if len(params[1]) == 0:
        return {"chatId": params[2].chatId,
                "message": f"""[cbiu]Info de {params[2].author.nickname}
[ci]Nickname: {params[2].author.nickname}
[ci]Id: {params[2].author.userId}
[ci]Reputación: {params[2].author.reputation}
[ci]Nivel: {params[2].author.level}
[Ciub]𝑷𝒂𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝒕𝒖𝒙 """}

    data = search_users(params[0], params[1][0])
    if not data.nickname:
        return {"chatId": params[2].chatId,
                "message": "No se han encontrado usuarios con ese nickname."}
    return {"chatId": params[2].chatId,
            "message": f"""[cbiu]Info de {data.nickname[0]}
[ci]Nickname: {data.nickname[0]}
[ci]Id: {data.userId[0]}
[ci]Reputación: {data.reputation[0]}
[ci]Nivel: {data.level[0]}
[Ciub]𝑷𝒂𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝒕𝒖𝒙 """}

def teach(*params):
    s = ""
    if len(params[1]) != 3:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 3 parámetros\nSe obtuvieron: {len(params[1])}"}
    if params[1][0].startswith(params[3]["SYM"]):
        s += "NOTA: Los comandos no deben empezar con el símbolo\n\n"
    if params[1][1] == '->':
        ccmd[params[1][0]] = params[1][2]
        f = open("modules/ccmd.json", "w")
        f.write(dumps(ccmd, indent=4))
        f.close()
        return {"chatId": params[2].chatId,
                "message": s+"Comando aprendido!"}
    else:
        return {"chatId": params[2].chatId,
                "message": "Error de sintaxis"}

def exe(*params):
    if params[1][0] in ccmd:
        return {"chatId": params[2].chatId,
                "message": ccmd[params[1][0]]}
    return {"chatId": params[2].chatId,
            "message": "El comando especificado no existe"}

def cmdel(*params):
    if params[1][0] in ccmd:
        ccmd.pop(params[1][0])
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}
    return {"chatId": params[2].chatId,
            "message": "El comando especificado no existe"}

def cmdir(*params):
    s = ""
    for i in ccmd:
        s += f"{i} -> {ccmd[i]}\n"
    return {"chatId": params[2].chatId,
            "message": s.strip()}

def alias(*params):
    if not len(params[1]):
        s = ""
        if not len(ALIAS):
            return {"chatId": params[2].chatId,
                    "message": "La lista está vacía"}
        for i in ALIAS:
            s += f"{i} -> {ALIAS[i]}\n"
        return {"chatId": params[2].chatId,
                "message": s.strip()}
    if len(params[1]) != 3:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 3 parámetros\nSe obtuvieron: {len(params[1])}"}
    if params[1][1] == '->':
        ALIAS[params[1][0]] = params[1][2]
    return {"chatId": params[2].chatId,
            "message": "Alias configurado!"}

def unalias(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Este comando espera recibir 1 parámetro.\nSe obtuvieron: {len(params[1])}"}
    if params[1][0] in ALIAS:
        ALIAS.pop(params[1][0])
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}
    else:
        return {"chatId": params[2].chatId,
                "message": "El alias especificado no existe."}

def var(*params):
    if not len(params[1]):
        s = ""
        if not len(VAR):
            return {"chatId": params[2].chatId,
                    "message": "La lista está vacía"}
        for i in VAR:
            s += f"{i} -> {VAR[i]}\n"
        return {"chatId": params[2].chatId,
                "message": s.strip()}
    if len(params[1]) != 3:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 3 parámetros\nSe obtuvieron: {len(params[1])}"}
    if params[1][1] == '->':
        VAR[params[1][0]] = params[1][2]
    return {"chatId": params[2].chatId,
            "message": "Variable configurada!"}


def unset(*params):
    if len(params[1]) < 1 or not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 parámetro\nSe obtuvieron: {len(params[1])}"}
    VAR.pop(params[1][0])
    return {"chatId": params[2].chatId,
            "message": "Variable eliminada!"}

def search_anime(*params):
    search = AnimeSearch(params[1][0]) 
    lang = 'es'
    translator = google_translator()
    translate_text = translator.translate(str(search.results[0].synopsis),lang_tgt=lang)
    return {"chatId": params[2].chatId,
            "message": f"\nCapitulos:{search.results[0].episodes} \nTitulo:{search.results[0].title}\nPuntaje:{search.results[0].score} \nSipnopsis:{translate_text}"}

def google(*params):
    return {"chatId": params[2].chatId,
            "message": f"https://www.google.com/search?q={parse.quote(params[1][0])}"}

def creador(*params):
    return {"chatId": params[2].chatId,
            "message": """
\n[ci]Mis creadores son Yuu y Darth Venom si quieres un bot como este o mejor coméntame en mi muro en mi perfil global
[ci]http://aminoapps.com/u/kyubi_yuu"""}

def glbal(*params):
    x = search_users(params[0], params[1][0], "uid")
    if not x:
        return {"chatId": params[2].chatId,
                "message": "Usuario no encontrado."}
    y = params[4].get_user_info(x).aminoId
    return {"chatId": params[2].chatId,
            "message": f"https://aminoapps.com/u/{y}"}

def globallink(subclient: object, *params):
    try:
        x = subclient.get_from_code(params[0][0]).objectId
        return {"chatId": params[1].chatId,
                "message": f"ndc://g/user-profile/"+f"{x}"}
    except:
        return {"chatId": params[1].chatId,
                "message": "Hubo un error en el proceso"}

def chiste(*params):
    chiste = c.get_random_chiste()
    return {"chatId": params[2].chatId,
            "message": chiste}

def chat(*params):
    translator = google_translator()
    translate_en = translator.translate(params[1][0], lang_tgt='en')
    params[1][0] = ''.join(map(str, translate_en))
    params[1][0] = params[1][0].strip("'")
    link = f"https://api.deltaa.me/chatbot?message={parse.quote(params[1][0])}&gender=Male"
    response = requests.get(link)
    json_data = json.loads(response.text)
    chatbot = translator.translate(json_data["message"], lang_tgt='es')
    return {"chatId": params[2].chatId,
            "message": chatbot}

def admin(*params):
    subclient = params[0]
    data = params[2]
    try:
        subclient.accept_host(params[2].chatId)
        return {"chatId": params[2].chatId,
                "message": "[Ciu]Ahora soy anfitrion de este chat, soy admin inclinense ante mi."}
    except:
        return {"chatId": params[2].chatId,
                "message": "Hubo un error en el proceso"}

def voz(*params):
    subclient = params[0]
    data = params[2]
    tts = gTTS((params[1][0]),lang="es")
    tts.save("voz.mp3")
    with open("voz.mp3", "rb") as file:
        subclient.send_message(params[2].chatId, file=file, fileType="audio")

def check_in(*params):
    subclient = params[0]
    data = params[2]
    try:
        days = subclient.get_user_checkins(subclient.profile.userId).consecutiveCheckInDays
        subclient.check_in()
        return {"chatId": params[2].chatId,
                "message": f"Check-in hecho! tienes {days} dias consecutivos!"}
    except: 
        return {"chatId": params[2].chatId,
                "message": f"Ya hiciste check in en esta comunidad numero de check-In consecutivos {days}"}

def lottery(*params):
    subclient = params[0]
    data = params[2]
    try:
        subclient.lottery()
        subclient.send_message(message="Loteria hecha con exito.",chatId=data.message.chatId)
    except:
        return {"chatId": params[2].chatId,
                "message": "ya hiciste la loteria en esta cuenta uwu"}

def joincomm(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": "Se esperaba obtener 1 parámetro. Se obtuvo 0"}
    aminoId = params[1][0]
    if aminoId.startswith('https://aminoapps.com/c/'):
        aminoId = params[1][0][24:]
    try:
        aminoId = params[4].search_community(aminoId).comId[0]
    except:
        return {"chatId": params[2].chatId,
                "message": "Comunidad no encontrada"}
    if aminoId in params[4].sub_clients().comId:
        return {"chatId": params[2].chatId,
                "message": "El bot ya fue unido a esa comunidad"}
    try:
        params[4].join_community(str(aminoId))
    except:
        return {"chatId": params[2].chatId,
                "message": "Ocurrió un error en el proceso y el bot no pudo unirse."}
    return {"chatId": params[2].chatId,
            "message": "Hecho!"}

def leavecomm(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": "Se esperaba obtener 1 parámetro. Se obtuvo 0"}
    aminoId = params[1][0]
    if aminoId == 'self':
        params[4].leave_community(params[0].comId)
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}
    elif aminoId.startswith('https://aminoapps.com/c/'):
        aminoId = params[1][0][24:]
    try:
        aminoId = params[4].search_community(aminoId).comId[0]
    except:
        return {"chatId": params[2].chatId,
                "message": "Comunidad no encontrada"}
    if aminoId in params[4].sub_clients().comId:
        params[4].leave_community(aminoId)
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}

def comment(*params):
    if len(params[1]) < 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 2 parámetro. Se obtuvieron: {len(params[1])}"}
    u = search_users(params[0], params[1][0], "uid")
    if not u:
        return {"chatId": params[2].chatId,
                "message": "Usuario no encontrado"}
    try:
        params[0].comment(userId=u, message=params[1][1])
    except:
        return {"chatId": params[2].chatId,
                "message": "Ocurrió un error en el proceso."}
    return {"chatId": params[2].chatId,
            "message": "Hecho!"}

def schedule(*params):
    if len(params[1]) < 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 2 parámetro. Se obtuvieron: {len(params[1])}"}
    if not re.match("[0-9]+[sm]", params[1][0]):
        return {"chatId": params[2].chatId,
                "message": "Error de sintaxis"}
    t = ""
    for i in params[1][0]:
        if i.isdigit():
            t += i
        if i == "s":
            break
        if i == "m":
            t = int(t)*60
            break
    t = int(t)
    params[5].message.content = params[1][1]
    Thread(target=timedexec, args=(params[6], params[5], t)).start()
    return {"chatId": params[2].chatId,
            "message": f"Se ha abierto un hilo para ejecutar un proceso en {params[1][0]}"}

def forange(*params):
    if len(params[1]) < 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 2 parámetro. Se obtuvieron: {len(params[1])}"}
    if params[1][0] == "config" and len(params[1]) == 2:
        t = [i.strip() for i in params[1][1].split(':')]
        if not t[1].isdigit():
            return {"chatId": params[2].chatId,
                    "message": "Se esperaba obtener un número pero se obtuvo un string."}
        CONFIGS[t[0]] = int(t[1])
        return {"chatId": params[2].chatId,
                "message": f"El valor de {t[0]} ha cambiado"}
    if not params[1][0].isdigit():
        return {"chatId": params[2].chatId,
                "message": "Se esperaba que el primer parámetro fuese un número entero."}
    if int(params[1][0]) > CONFIGS['forange-setime']:
        return {"chatId": params[2].chatId,
                "message": f"Por motivos de seguridad el rango de repeticiones se ha limitado a {CONFIGS['forange-setime']}"}
    params[5].message.content = params[1][1]
    for i in range(int(params[1][0])):
        params[6](params[5])
    return {"chatId": params[2].chatId,
            "message": ""}

def horamundial(*params):
    if len(params[1]) == 2:
        if params[1][0] == "search":
            rtz = params[1][1].replace(' ', '_')
            s = ""
            for i in pytz.all_timezones:
                if re.match(f"(.+)?/?{rtz.lower()}(.+)?/?", i.lower()):
                    s += f"{i}\n"
            return {"chatId": params[2].chatId,
                    "message": s}
        if params[1][0] == "capital":
            q = f"capital de {params[1][1]}"
            print(q)
            r = requests.get(f"https://google.com/search?q={parse.quote(q)}")
            s = re.search('<div class="BNeawe deIvCb AP7Wnd">[^<>]+</div>', r.text)
            s = s.group().replace('<div class="BNeawe deIvCb AP7Wnd">', "").replace("</div>", "")
            return {"chatId": params[2].chatId,
                    "message": s}
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 1 parámetro Se obtuvieron: {len(params[1])}"}
    rtz = sintilde(params[1][0].replace(' ', '_'))
    tz = ""
    for i in pytz.all_timezones:
        if rtz.lower() in i.lower():
            tz = i
            break
    if not tz:
        return {"chatId": params[2].chatId,
                "message": "Zona horaria desconocida"}
    format = "%H:%M:%S"
    utc = datetime.now(pytz.timezone('UTC'))
    rtz = utc.astimezone(pytz.timezone(tz))
    return {"chatId": params[2].chatId,
            "message": rtz.strftime(format)}

def die(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    _exit(0)

def cat(*params):
    r = requests.get("https://api.thecatapi.com/v1/images/search?limit=1&page=10&order=Desc")
    r = requests.get(r.json()[0]['url'])
    b = BytesIO(r.content)
    return {"chatId": params[2].chatId,
            "file": b,
            "fileType": "image"}

def quiet(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 argumento. Se obtuvieron: {len(params[1])}"}
    params = list(params)
    params[1] = split(params[1][0])
    cmd = params[1][0][1:]
    params[1] = params[1][1:]
    r = CMDS[cmd](*params)
    return {"chatId": params[2].chatId,
            "message": ""}

def caen(*params):
    if not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener como mínimo 1 argumento. Se obtuvieron: {len(params[1])}"}
    elif len(params[1]) > 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener como máximo 2 argumentos. Se obtuvieron {len(params[1])}"}
    elif len(params[1]) == 1:
        return {"chatId": params[2].chatId,
                "message": caesar.caen(params[1][0], 0)}
    if not params[1][1].isdigit:
        return {"chatId": params[2].chatId,
                "message": "La clave debe ser un número"}
    return {"chatId": params[2].chatId,
            "message": caesar.caen(params[1][0], int(params[1][1]))}

def cade(*params):
    if not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener como mínimo 1 argumento. Se obtuvieron: {len(params[1])}"}
    elif len(params[1]) > 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener como máximo 2 argumentos. Se obtuvieron {len(params[1])}"}
    elif len(params[1]) == 1:
        return {"chatId": params[2].chatId,
                "message": caesar.cade(params[1][0], 0)}
    if not params[1][1].isdigit:
        return {"chatId": params[2].chatId,
                "message": "La clave debe ser un número"}
    return {"chatId": params[2].chatId,
            "message": caesar.cade(params[1][0], int(params[1][1]))}

def bine(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 argumento. Se obtuvieron: {len(params[1])}"}
    return {"chatId": params[2].chatId,
            "message": binen.binen(params[1][0])}

def binde(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 argumento. Se obtuvieron: {len(params[1])}"}
    return {"chatId": params[2].chatId,
            "message": binen.bindec(params[1][0])}

def b64e(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 argumento. Se obtuvieron: {len(params[1])}"}
    return {"chatId": params[2].chatId,
            "message": base64.b64encode(params[1][0].encode('utf-8')).decode('utf-8')}

def b64d(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 argumento. Se obtuvieron: {len(params[1])}"}
    return {"chatId": params[2].chatId,
            "message": base64.b64decode(params[1][0].encode('utf-8')).decode('utf-8')}

def blkl(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if not len(params[1]):
        s = ""
        for i in BLKL:
            s += f"- {i}\n"
        return {"chatId": params[2].chatId,
                "message": s.strip()}
    if len(params[1]) != 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 2 argumentos. Se obtuvieron: {len(params[1])}"}
    if params[1][0] == "lock":
        if params[1][1] == "blkl":
            return {"chatId": params[2].chatId,
                    "message": "Buen intento, pero no puedes bloquear el comando blkl"}
        if CMDS.get(params[1][1]):
            BLKL[params[1][1]] = CMDS.pop(params[1][1])
        else:
            return {"chatId": params[2].chatId,
                    "message": "El comando especificado no existe"}
    elif params[1][0] == "unlock":
        if params[1][1] == "blkl":
            return {"chatId": params[2].chatId,
                    "message": "Buen intento, pero no puedes bloquear el comando blkl"}
        if BLKL.get(params[1][1]):
            CMDS[params[1][1]] = BLKL.pop(params[1][1])
        else:
            return {"chatId": params[2].chatId,
                    "message": "El comando especificado no existe"}
    else:
        return {"chatId": params[2].chatId,
                "message": "La opción especificada es inexistente"}
    return {"chatId": params[2].chatId,
            "message": "¡Hecho!"}

def dolararg(*params):
    d = dolar.dolararg()
    return {"chatId": params[2].chatId,
            "message": f"[CB]Dólar Blue\n[B]Compra   Venta\n[i]   {d['Dólar Blue'][0]}        {d['Dólar Blue'][1]}\n\n[CB]Dólar Oficial\n[B]Compra   Venta\n[i]   {d['Dólar Oficial'][0]}        {d['Dólar Oficial'][1]}\n\n[CB]Dólar Bolsa\n[B]Compra   Venta\n[i]   {d['Dólar Bolsa'][0]}        {d['Dólar Bolsa'][1]}"}

def euroarg(*params):
    d = dolar.euroarg()
    return {"chatId": params[2].chatId,
            "message": f"[CB]Euro\n[B]Compra   Venta\n[i]   {d[0]}        {d[1]}"}

def delegate(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}

    if not len(params[1]) or len(params[1]) < 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 parámetro. Se obtuvieron: {len(params[1])}"}
    data = search_users(params[0], params[1][0], "uid")
    if data:
        params[3]["ADMIN"].append(data)
        f = open('data', 'w')
        f.write(dumps(params[3], indent=4))
        f.close()
    else:
        return {"chatId": params[2].chatId,
                "message": "El usuario especificado no existe."}
    return {"chatId": params[2].chatId,
            "message": "Hecho!"}

def relegate(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if not len(params[1]) or len(params[1]) < 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 parámetro. Se obtuvieron: {len(params[1])}"}
    data = search_users(params[0], params[1][0], "uid")
    if data:
        params[3]["ADMIN"].pop(params[3]["ADMIN"].index(data))
        f = open('data', 'w')
        f.write(dumps(params[3], indent=4))
        f.close()
    else:
        return {"chatId": params[2].chatId,
                "message": "El usuario especificado no existe."}
    return {"chatId": params[2].chatId,
            "message": "Hecho!"}


def coins(*params):
    subclient = params[0]
    data = params[2]
    coins=int(subclient.get_wallet_info().totalCoins)
    return {"chatId": params[2].chatId,
            "message": f"mi total de coins : {coins}"}


def onstart(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if len(params[1]) > 2:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener máximo 2 parámetros. Se obtuvieron: {len(params[1])}"}
    elif not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener mínimo 1 parámetro. Se obtuvieron: {len(params[1])}"}
    if params[1][0] == "add":
        try:
            f = open("modules/onstart.json", 'r')
        except FileNotFoundError:
            f = open("modules/onstart.json", 'w+')
        d = []
        try: d = load(f)
        except: pass
        f.close()
        d.append([params[1][1], {"userId": params[2].author.userId, "nickname": params[2].author.nickname,"chatId": params[2].chatId, "comId": params[5].comId}])
        f = open("modules/onstart.json", 'w')
        f.write(dumps(d, indent=4));f.close()
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}
    if params[1][0] == "del":
        cmd = split(params[1][1])
        cmd = cmd[0][1:]
        try:
            f = open("modules/onstart.json", 'r')
        except FileNotFoundError:
            f = open("modules/onstart.json", 'w+')
        d = []
        try: d = load(f)
        except: pass
        f.close()
        if not params[1][1].isdigit():
            return {"chatId": params[2].chatId,
                    "message": f"Se esperaba obtener un número, se obtuvo: {params[1][1]}"}
        if not int(params[1][1]) in range(len(d)):
            return {"chatId": params[2].chatId,
                    "message": "La línea especificada no existe"}
        x = d.pop(int(params[1][1]))
        f = open("modules/onstart.json", 'w')
        f.write(dumps(d, indent=4));f.close()
        return {"chatId": params[2].chatId,
                "message": f"Se eliminó: {params[1][1]}"}
    if params[1][0] == "show":
        try:
            f = open("modules/onstart.json")
        except FileNotFoundError:
            f = open("modules/onstart.json", 'w+')
        d = []
        try: d = load(f)
        except: pass
        f.close()
        if not len(d):
            return {"chatId": params[2].chatId,
                    "message": "La lista está vacía"}
        s = ""
        for i in range(len(d)):
            s += f"{i}: {d[i][0]}\n"
        return {"chatId": params[2].chatId,
                "message": s.strip()}

def floadu(sf):
    exec(sf)
    return locals()[sf.split()[1].split('(')[0]]

def fload(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if len(params[1]) != 3:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 3 parámetros. Se obtuvieron: {len(params[1])}"}
    try:
        exec(params[1][2])
    except:
        return {"chatId": params[2].chatId,
                "message": traceback.format_exc()}
    CMDS[params[1][0]] = locals()[params[1][1]]
    lcmd = load(open("modules/load.json"))
    lcmd[params[1][0]] = params[1][2]
    f = open("modules/load.json", "w")
    f.write(dumps(lcmd, indent=4))
    f.close()
    return {"chatId": params[2].chatId,
            "message": f"{params[1][0]} ha sido cargado con éxito"}

def unload(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaban obtener 1 parámetros. Se obtuvieron: {len(params[1])}"}
    if params[1][0] in CMDS:
        CMDS.pop(params[1][0])
        lcmd = load(open("modules/load.json"))
        if params[1][0] in lcmd:
            lcmd = load(open("modules/load.json"))
            lcmd.pop(params[1][0])
            f = open("modules/load.json", "w")
            f.write(dumps(lcmd, indent=4))
            f.close()
        return {"chatId": params[2].chatId,
                "message": "Hecho!"}
    else:
        return {"chatId": params[2].chatId,
                "message": "El comando solicitado no existe."}


def comlist(*params):
    if len(params[1]) > 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    if len(params[1]) and params[1][0] == "id":
        s = ""
        for i in params[4].sub_clients().aminoId:
            s += f"{i}\n"
        return {"chatId": params[2].chatId,
                "message": s.strip()}
    s = ""
    for i in params[4].sub_clients().name:
        s += f"{i}\n"
    return {"chatId": params[2].chatId,
            "message": s.strip()}

def kick(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    uid = search_users(params[0], params[1][0], "uid")
    uuid = params[2].author.userId
    if uid in KICK:
        if params[2].chatId in KICK[uid]:
            if uuid in KICK[uid][params[2].chatId]:
                return {"chatId": params[2].chatId,
                        "message": "Ya has solicitado un kick a este usuario en este chat."}
            if params[2].author.level > 7:
                KICK[uid][params[2].chatId].append(uuid)
            else:
                return {"chatId": params[2].chatId,
                        "message": "El nivel mínimo para solicitar un kick es 7."}
        else:
            if params[2].author.level > 7:
                KICK[uid][params[2].chatId] = [uuid]
            else:
                return {"chatId": params[2].chatId,
                        "message": "El nivel mínimo para solicitar un kick es 7."}
    else:
        KICK[uid] = {params[2].chatId: [uuid]}
    if len(KICK[uid][params[2].chatId]) == 4 or params[2].author.role in (100, 101, 102):
        params[0].kick(userId=uid, chatId=params[2].chatId, allowRejoin=False)
        KICK.pop(uid)
        return {"chatId": params[2].chatId,
                "message": f"El usuario {params[1][0]} ha sido expulsado del chat."}
    else:
        return {"chatId": params[2].chatId,
                "message": "Tu solicitud ha sido registrada."}

def golpear(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    p = random.choices(["le rompió la cara a", "le bajó los dientes a", "cagó a trompadas a", "le partió la madre a"])[0]
    return {"chatId": params[2].chatId,
            "message": f"{params[2].author.nickname} {p} {params[1][0]}"}


def matar(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    p = random.choices(["pulverizó a piñas a", "desintegró a", "despedazó y escondió en una bolsa a", "fusiló a"])[0]
    return {"chatId": params[2].chatId,
            "message": f"{params[2].author.nickname} {p} {params[1][0]}"}

def vrtion(*params):
    if len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"No se esperaba obtener ningún parámetro.\nSe obtuvieron: {len(params[1])}"}
    return {"chatId": params[2].chatId,
            "message": VERSION}

def unete(subclient, *params):
    if not params[1].author.userId in params[2]["ADMIN"]:
        return {"chatId": params[1].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    try:
        subclient.join_chat(chatId=params[2].chatId)
        return {"chatId": params[2].chatId,
                "message": f"buenas"}
    except: 
        return {"chatId": params[2].chatId,
                "message": f"fallo en la matrix"}


def sug(*params):
    try:
        if not len(params[1]):
            return {"chatId": params[2].chatId,
                    "message": "Se esperaba obtener al menos 1 argumento."}
        if len(params[1]) > 2:
            return {"chatId": params[2].chatId,
                    "message": f"Se esperaba obtener un máximo de 2 argumentos.\nSe obtuvieron: {len(params[1])}"}
        if params[1][0] == "add":
            if len(params[1]) != 2:
                return {"chatId": params[2].chatId,
                        "message": f"Se esperaba obtener 2 argumentos.\nSe obtuvieron: {len(params[1])}"}
            TDATA["sug"].append(params[1][1])
            update()
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        if params[1][0] == "del":
            if not params[2].author.userId in params[3]["ADMIN"]:
                return {"chatId": params[2].chatId,
                        "message": "No tienes permisos suficientes para ejecutar esta acción."}
            if len(params[1]) != 2:
                return {"chatId": params[2].chatId,
                        "message": f"Se esperaba obtener 2 argumentos.\nSe obtuvieron: {len(params[1])}"}
            TDATA["sug"].pop(int(params[1][1]))
            update()
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        if params[1][0] == "show":
            if len(params[1]) != 1:
                return {"chatId": params[2].chatId,
                        "message": f"Se esperaba obtener 1 argumento.\nSe obtuvieron: {len(params[1])}"}
            s = ""
            if not len(TDATA["sug"]):
                return {"chatId": params[2].chatId,
                        "message": "La lista está vacía"}
            for i in range(len(TDATA["sug"])):
                s += f"{i}. {TDATA['sug'][i]}\n"
            return {"chatId": params[2].chatId,
                    "message": s.strip()}
        else:
            return {"chatId": params[2].chatId,
                    "message": "Opción desconocida"}
    except Exception:
        return {"chatId": params[2].chatId,
                "message": str(traceback.format_exc())}


def chocolate(*params):
    if len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"No se esperaba obtener ningún argumento.\nSe obtuvieron {len(params[1])}"}
    n = random.randint(1, len(listdir('media')))
    f = open(f"media/chocolate{n}.gif", 'rb')
    return {"chatId": params[2].chatId,
            "fileType": "gif",
            "file": f,
            "embedContent": f"{params[2].author.nickname[:28]} se comió un chocolate",
            "embedTitle": "Chocolate~"}


def ad(*params):
    subclient = params[0]
    data = params[2]
    try:
        subclient.watch_ad()
        return {"chatId": params[2].chatId,
                "message": f"anuncio visto!"}
    except: 
        return {"chatId": params[2].chatId,
                "message": f"fallo en la matrix"} 

def yt(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener 1 único argumento.\nSe obtuvieron: {len(params[1])}"}
    params[1][0] = sintilde(params[1][0])
    r = requests.get(f"https://www.youtube.com/results?search_query={parse.quote(params[1][0])}")
    c = r.text.find('accessibilityData')
    s = r.text[c:c+400]
    s = eval(re.findall('\{"label":[^}]+\}', s)[0])
    q = s['label'][:re.search('de .+ hace [0-9]', s['label']).start()].strip()
    author = re.sub(' hace [0-9]', '', re.findall('de .+ hace [0-9]', s['label'])[0][3:])
    c = r.text.find('"thumbnails"')
    s = r.text[c:c+500]
    s = eval(re.findall('\[[^\]]+\]', s)[0])[0]['url'].split('?')[0]
    f = BytesIO(requests.get(s).content)
    c = r.text.find('"lengthText"')
    s = r.text[c:c+800]
    c = s.find('"webCommandMetadata"')
    s = s[c:c+500]
    s = eval(re.findall('\{"url":[^}]+\}', s)[0])
    print(f"Video: https://youtube.com{s['url']}")
    return {"chatId": params[2].chatId,
            "message": "Youtube search",
            "embedImage": f,
            "embedContent": q,
            "embedLink": f"https://youtube.com{s['url']}",
            "embedTitle": author}

def antiraid(*params):
    #antiraid policy show
    #antiraid policy 1:True
    if not params[2].author.userId in params[3]["ADMIN"]:
        return {"chatId": params[2].chatId,
                "message": "No tienes permisos suficientes para ejecutar esta acción."}
    if not len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba al menos 1 parámetro.\nSe obtuvieron {len(params[1])}"}
    if params[1][0] == "ad":
        if len(params[1]) != 2:
            return {"chatId": params[2].chatId,
                    "message": f"Se esperaba obtener 2 parámetros.\nSe obtuvieron {len(params[1])}"}
        if params[1][1] in ("True", "1"):
            if params[5].comId in ANTIRAID["trueat"]["normal"] or params[5].comId in ANTIRAID["trueat"]["special"]:
                return {"chatId": params[2].chatId,
                        "message": "El antiraid ya está activado en esta comunidad."}
            ANTIRAID["trueat"]["normal"].append(params[5].comId)
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        elif params[1][1] in ("False", "0"):
            if not params[5].comId in ANTIRAID["trueat"]["normal"]:
                return {"chatId": params[2].chatId,
                        "message": "El antiraid 'ad' no está activado en esta comunidad."}
            ANTIRAID["trueat"]["normal"].pop(ANTIRAID["trueat"]["normal"].index(params[5].comId))
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        else:
            return {"chatId": params[2].chatId,
                    "message": "Valor inválido."}
    elif params[1][0] == "sp":
        if len(params[1]) != 2:
            return {"chatId": params[2].chatId,
                    "message": f"Se esperaba obtener 2 parámetros.\nSe obtuvieron {len(params[1])}"}
        if params[1][1] in ("True", "1"):
            if params[5].comId in ANTIRAID["trueat"]["special"] or params[5].comId in ANTIRAID["trueat"]["normal"]:
                return {"chatId": params[2].chatId,
                        "message": "El antiraid ya está activado en esta comunidad."}
            ANTIRAID["trueat"]["special"].append(params[5].comId)
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        elif params[1][1] in ("False", "0"):
            if not params[5].comId in ANTIRAID["trueat"]["special"]:
                return {"chatId": params[2].chatId,
                        "message": "El antiraid 'sp' no está activado en esta comunidad."}
            ANTIRAID["trueat"]["special"].pop(ANTIRAID["trueat"]["special"].index(params[5].comId))
            return {"chatId": params[2].chatId,
                    "message": "Hecho!"}
        else:
            return {"chatId": params[2].chatId,
                    "message": "Valor inválido."}
    elif params[1][0] == "status":
        if len(params[1]) != 1:
            return {"chatId": params[2].chatId,
                    "message": "status no recibe opciones"}
        if params[5].comId in ANTIRAID["trueat"]["normal"]:
            return {"chatId": params[2].chatId,
                    "message": "El antiraid 'ad' está activo en esta comunidad."}
        elif params[5].comId in ANTIRAID["trueat"]["special"]:
            return {"chatId": params[2].chatId,
                    "message": "El antiraid 'sp' está activo en esta comunidad."}
        else:
            return {"chatId": params[2].chatId,
                    "message": "El antiraid está desactivado en esta comunidad."}
    elif params[1][0] == "white":
        if len(params[1]) != 3:
            return {"chatId": params[2].chatId,
                    "message": f"Se esperban obtener 3 parámetro.\nSe obtuvieron {len(params[1])}"}
        if params[1][1] == "add":
            data = search_users(params[0], params[1][2], "uid")
            if not data:
                return {"chatId": params[2].chatId,
                        "message": "No se han encontrado usuarios con ese nickname."}
            if data in ANTIRAID["white"]:
                return {"chatId": params[2].chatId,
                        "message": "El usuario ya está en la white-list."}
            ANTIRAID["white"].append(data)
            return {"chatId": params[2].chatId,
                    "message": "¡Hecho!"}
        elif params[1][1] == "del":
            data = search_users(params[0], params[1][2], "uid")
            if not data:
                return {"chatId": params[2].chatId,
                        "message": "No se han encontrado usuarios con ese nickname."}
            if not data in ANTIRAID["white"]:
                return {"chatId": params[2].chatId,
                        "message": "El usuario no está en la white-list."}
            ANTIRAID["white"].pop(ANTIRAID["white"].index(data))
            return {"chatId": params[2].chatId,
                    "message": "¡Hecho!"}
        else:
            return {"chatId": params[2].chatId,
                    "message": "antiraid: white: La opción especificada no existe."}
    else:
        return {"chatId": params[2].chatId,
                "message": "antiraid: La opción especificada no existe."}

def golpear(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    p = random.choices(["le rompió la cara a", "le bajó los dientes a", "cagó a trompadas a", "le partió la madre a"])[0]
    n = random.randint(1, len(listdir('media/golpear')))
    f = open(f"media/golpear/golpe{n}.gif", 'rb')
    return {"chatId": params[2].chatId,
            "fileType": "gif",
            "file": f,
            "embedContent": f"{p} {params[1][0]}",
            "embedTitle": f"{params[2].author.nickname}"}

def matar(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    p = random.choices(["pulverizó a piñas a", "desintegró a", "despedazó y escondió en una bolsa a", "fusiló a"])[0]
    n = random.randint(1, len(listdir('media/matar')))
    f = open(f"media/matar/matar{n}.gif", 'rb')
    return {"chatId": params[2].chatId,
            "fileType": "gif",
            "file": f,
            "embedContent": f"{p} {params[1][0]}",
            "embedTitle": f"{params[2].author.nickname}"}

def mimir(*params):
    if len(params[1]):
        return {"chatId": params[2].chatId,
                "message": f"No se esperaba obtener ningún argumento.\nSe obtuvieron {len(params[1])}"}
    n = random.randint(1, len(listdir('media/dormir')))
    f = open(f"media/dormir/dormir{n}.gif", 'rb')
    return {"chatId": params[2].chatId,
            "fileType": "gif",
            "file": f,
            "embedContent": f"{params[2].author.nickname[:28]} se mimio",
            "embedTitle": "hagamos la mimision"}

def abrazar(*params):
    if len(params[1]) != 1:
        return {"chatId": params[2].chatId,
                "message": f"Se esperaba obtener un máximo de 1 argumento.\nSe obtuvieron {len(params[1])}"}
    p = random.choices(["ha apapuchado a", "Abrazo fuertemente a", "Abrazo lleno de amor a", "le da un cálido abrazo a"])[0]
    n = random.randint(1, len(listdir('media/abrazo')))
    f = open(f"media/abrazo/abrazo{n}.gif", 'rb')
    return {"chatId": params[2].chatId,
            "fileType": "gif",
            "file": f,
            "embedContent": f"{p} {params[1][0]}",
            "embedTitle": f"{params[2].author.nickname}"}

def miid(*params):
    return rut(params[2], params[2].author.userId)

def revivir(*params):
    if not len(params[1]):
        return rut(params[2], "%s ha vuelto a la vida" % params[2].author.nickname)
    return rut(params[2], "%s resucitó a %s" % (params[2].author.nickname, params[1][0]))

def plat(*params):
    return rut(params[2], platform)

def uname(*params):
    return rut(params[2], popen("uname -a").read())

def chver(*params):
    if not params[2].author.userId in params[3]["ADMIN"]:
        return rut(params[2], "No tienes permisos suficientes para ejecutar esta acción.")
    if len(params[1]):
        global VERSION
        VERSION = params[1][0]
    return rut(params[2], VERSION)

def dar(*params):
	try:
		if len(params[1]) < 2:
			return rut(params[2], "Se esperaba obtener un argumento por lo menos dos argumentos")
		if params[1][0] == "add":
			if len(params[1]) != 3:
				return rut(params[2], "Se esperaba obtener 3 argumentos")
			if not TDATA["dar"]:
				TDATA["dar"].append({})
				update()
			if not p[1][1] in TDATA["dar"]:
				TDATA["dar"][0][params[1][1]] = params[1][2]
				update()
				return rut(params[2], "¡Listo! Ahora puedes dar %s" % params[1][1])
			else:
				return rut(params[2], "%s no está en la lista de las cosas que puedes dar" % params[1][1])
		if params[1][0] == "del":
			if len(params[1]) != 2:
				return rut(params[2], "Se esperaba obtener 2 argumentos")
			if params[1][1] in TDATA["dar"][0]:
				TDATA["dar"][0].pop(params[1][1])
				update()
				return rut(params[2], "Ya no puedes dar %s" % params[1][1])
			else:
				return rut(params[2], "%s no está en la lista de las cosas que puedes dar" % params[1][1])
		return rut(params[2], "%s le dio %s a %s" % (params[2].author.nickname, TDATA["dar"][0][params[1][0]], params[1][1]))
	except Exception:
			return rut(params[2], traceback.format_exc())

def idg(*params):
    try:
        if not len(params[1]):
            return rut(params[2], "Se esperaba obtener un argumento")
        if re.match("https?://aminoapps\.com/c/", params[1][0]):
            aminoId=re.split("https?://aminoapps\.com/c/", params[1][0])[1]
            return rut(params[2], str(params[4].search_community(aminoId).comId[0]))
        elif re.match("https?://aminoapps\.com/[a-z]/", params[1][0]):
            return rut(params[2], params[4].get_from_code(params[1][0]).objectId)
    except Exception:
        return rut(params[2], traceback.format_exc())

def entretenimiento(*params):
    return {"chatId": params[2].chatId,
            "message": """
[cb]「 ꗃ 有 𝙀𝙣𝙩𝙧𝙚𝙩𝙚𝙣𝙞𝙢𝙞𝙚𝙣𝙩𝙤...
[Ic]/ping /dare /truth

[Ic]/info /anime /search

[Ic] /chiste /voz /chat /cat

[Ic]/comment /binen /binde

[Ic]/b6aen /b64de /kick

[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}

def dueño(*params):
    return {"chatId": params[2].chatId,
            "message": """[cb]︒ 「 ꗃ 日 𝘿𝙪𝙚𝙣̃𝙤... 
[Ic]/fotop /nick /bio

[Ic]/join /leave /load 

[Ic]/unload /delegar /relegar

[Ic]/joinc leavec /rm

[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}

def acciones(*params):
    return {"chatId": params[2].chatId,
            "message": """
[cb]︒ 「 ꗃ 所 𝘼𝙘𝙘𝙞𝙤𝙣𝙚𝙨... 
[Ic]/golpear /abrazar /chocolate

[Ic]/matar /mimir

[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}

def ayudante(*params):
    return {"chatId": params[2].chatId,
            "message": """
[cb]︒ 「 ꗃ 日 𝘼𝙮𝙪𝙙𝙖𝙣𝙩𝙚... 
[Ic]/admin /tra /coins

[Ic]/checkin /loteria /idg

[Ic]/version /creador /blkl

[Ic]/global /globallink /antiraid

[Ic]/comlist..

[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}

def comunes(*params):
    return {"chatId": params[2].chatId,
            "message": """
[cb]︒ 「 ꗃ 有 𝘾𝙤𝙢𝙪𝙣𝙚𝙨... 
[Ic]/for /schedule /random

[Ic]/choice /alias /unalias

[Ic]/var /quiet /unete 

[Ic]/clock /unete..

[C]©𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝒃𝒚 𝑻𝑼𝑿"""}

def todos(*params):
    people = params[0].get_chat_users(params[2].chatId,size=1000).userId
    users = []
    for usersin in people:
        users.append(usersin)
        print(users)
        return {"chatId": params[2].chatId,
                "message": f"<$@{params[1][0]}$>",
                "mentionUserIds":users}

def follow(*params):
        x = params[0].get_from_code(params[1][0]).objectId
        b = params[0].get_user_info(userId=x)
        c = b.nickname
        params[0].follow(userId=x)
        return {"chatId": params[2].chatId,
                "message": f"he seguido a {c}"}

def unfollow(*params):
        x = params[0].get_from_code(params[1][0]).objectId
        b = params[0].get_user_info(userId=x)
        c = b.nickname
        params[0].unfollow(userId=x)
        return {"chatId": params[2].chatId,
                "message": f"he dejado de seguir a {c}"}

CMDS = {
    'nick': chnick,
    'bio': chbio,
    'fotop': chprofpic,
    'echo': echo,
    'join': join,
    'leave': leave,
    'rm': rm,
    'choice': choice,
    'random': rand,
    'truth': truth,
    'dare': dare,
    'math': newton,
    'ping': ping,
    'help': hlp,
    'info': info,
    'teach': teach,
    'exec': exe,
    'cmdel': cmdel,
    'cmdir': cmdir,
    'alias': alias,
    'unalias': unalias,
    'var': var,
    'unset': unset,
    'anime': search_anime,
    'search': google,
    'creador': creador,
    'global': glbal,
    'globallink': globallink,
    'chiste': chiste,
    'chat': chat,
    'admin': admin,
    'voz': voz,
    'checkin': check_in,
    'loteria': lottery,
    'joinc': joincomm,
    'leavec': leavecomm,
    'comment': comment,
    'schedule': schedule,
    'for': forange,
    'clock': horamundial,
    'die': die,
    'cat': cat,
    'quiet': quiet,
    'caen': caen,
    'cade': cade,
    'binen': bine,
    'binde': binde,
    'b64en': b64e,
    'b64de': b64d,
    'blkl': blkl,
    'dolar': dolararg,
    'euro': euroarg,
    'delegar': delegate,
    'relegar': relegate,
    'coins': coins,
    'onstart': onstart,
    'load': fload,
    'unload': unload,
    'comlist': comlist,
    'kick': kick,
    'golpear': golpear,
    'matar': matar,
    'version': vrtion,
    'unete': unete,
    'sugerencia': sug,
    'chocolate': chocolate,
    'ad': ad,
    'yt': yt,
    'antiraid': antiraid,
    'mimir': mimir,
    'abrazar': abrazar,
    'miid': miid,
    'revivir': revivir,
    'platform': plat,
    'uname': uname,
    'chver': chver,
    'dar': dar,
    'idg': idg,
    'entretenimiento': entretenimiento,
    'dueño': dueño,
    'ayudante': ayudante,
    'comunes': comunes,
    'acciones': acciones,
    'todos': todos,
    'follow': follow,
    'unfollow': unfollow
}

ALIAS = {}

VAR = {
        'father': "Darth Venom"
        }

CONFIGS = {
        'forange-setime': 5
        }

FUNCTIONS = {}  # Coming Soon

TDATA = {
        'sug': [],
        'dar': []
        }

WELCOME = ""

BLKL = {}

KICK = {}

BAN = {}

ANTIRAID = {
        "white": ["47c81c88-6203-4f13-b9d6-260e24d7e466"],
        "policy": {},
        "trueat": {"normal": [], "special": []}
        }

if "load.json" in listdir("modules"):
    lcmd = open("modules/load.json")
    if lcmd.read():
        lcmd.seek(0)
        lcmd = load(lcmd)
        for i in lcmd:
            CMDS[i] = floadu(lcmd[i])
    else:
        lcmd.close()
        lcmd = open("modules/load.json", "w+")
        lcmd.write('{}')
        lcmd.close()
else:
    lcmd = open("modules/load.json", "w+")
    lcmd.write('{}')
    lcmd.close()

ftdata = open("modules/data.json")
TDATA = load(ftdata)
ftdata.close()
