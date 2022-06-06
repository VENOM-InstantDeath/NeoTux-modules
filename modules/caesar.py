a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def sintilde(x):
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

def caen(s: str, k: int) -> str:
    o = ""
    for i in s:
        if i.islower():
            o += a[a.index(i) + k]
        elif i.isupper():
            o += a[a.index(i) + k].upper()
        else:
            o += i
    return o

def cade(s: str, k: int) -> str:
    o = ""
    for i in s:
        if i.islower():
            o += a[a.index(i) - k]
        elif i.isupper():
            o += a[a.index(i) - k].upper()
        else:
            o += i
    return o

