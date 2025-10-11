from base64 import b64encode,b64decode,b85encode,b85decode,b16encode,b16decode,a85encode,a85decode,b32encode,b32decode

def Zenc(msg):
    msgUNI = ''
    for char in msg:
        msgUNI=msgUNI+str(ord(char))+' '
    message_bytes = msgUNI.encode('utf-8')
    b64 = b64encode(message_bytes)
    b85 = b85encode(b64)
    b16 = b16encode(b85)
    b32 = b32encode(b16)
    a85 = a85encode(b32)
    out = a85.decode('ascii')
    msgUNI = ''
    for char in out:
        msgUNI = msgUNI + str(ord(char)) + ' '
    message_bytes = msgUNI.encode('utf-8')
    b64 = b64encode(message_bytes)
    b85 = b85encode(b64)
    b16 = b16encode(b85)
    b32 = b32encode(b16)
    a85 = a85encode(b32)
    out = a85.decode('ascii')
    msgUNI = ''
    for char in out:
        msgUNI = msgUNI + str(ord(char)) + ' '
    return msgUNI

def Zdec(b64BYTE):
    numbers = ''.join(c if c.isdigit() else ' ' for c in b64BYTE).split()
    out = ''
    for num in numbers:
        out = out + chr(int(num))
    base64_bytes = out.encode('utf-8')
    a85 = a85decode(base64_bytes)
    b32 = b32decode(a85)
    b16 = b16decode(b32)
    b85 = b85decode(b16)
    b64 = b64decode(b85)
    ou = b64.decode('utf-8')
    numbers = ''.join(c if c.isdigit() else ' ' for c in ou).split()
    out = ''
    for num in numbers:
        out = out+chr(int(num))
    base64_bytes = out.encode('utf-8')
    a85 = a85decode(base64_bytes)
    b32 = b32decode(a85)
    b16 = b16decode(b32)
    b85 = b85decode(b16)
    b64 = b64decode(b85)
    ou = b64.decode('utf-8')
    numbers = ''.join(c if c.isdigit() else ' ' for c in ou).split()
    out = ''
    for num in numbers:
        out = out + chr(int(num))
    return out

def NENC(msg):
    msg_bytes = msg.encode("utf-8")
    b64 = b64encode(msg_bytes)
    out = b64.decode("ascii")
    return out

def NDEC(b64B):
    b = b64B.encode("utf-8")
    b64 = b64decode(b)
    out = b64.decode("utf-8")
    return out

class zs():
    def __init__(self, *, path,ENCODING):
        self.__path = path
        self._enc = ENCODING

    def read(self):
        x = open(self.__path, "r")
        d = []
        strochaks = []
        b = ''
        c = x.readlines()
        z = len(c)
        for m in range(z):
            for v in c[int(m)]:
                d.append(v)
            d.remove('\n')
            for s in range(len(d)):
                b = b + str(d[s])
            if self._enc == True:
                strochaks.append(Zdec(b))
            elif self._enc == False:
                strochaks.append(b)
            d = []
            b = ''
        x.close()
        return strochaks

    def write(self, acc, pa, app):
        x = open(self.__path, "a")
        x.write(f"{Zenc(acc)}\n{Zenc(pa)}\n{Zenc(app)}\n")
        x.close()