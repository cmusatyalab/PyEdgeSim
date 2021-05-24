import math
def ipno2ipadd(ipno):
    if math.isnan(ipno):
        ipno = 0
    w = int ( ipno / 16777216 ) % 256
    x = int ( ipno / 65536    ) % 256
    y = int ( ipno / 256      ) % 256
    z = int ( ipno            ) % 256
    return "{}.{}.{}.{}".format(w,x,y,z)
def ipadd2ipno(ipadd):
    w,x,y,z = ipadd.split('.')
    retipno = int(w) * 16777216 + int(x) * 65536 + int(y) * 256 + int(z)
    return retipno

def isip(strin):
    a = strin.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i >255:
            return False
    return True

