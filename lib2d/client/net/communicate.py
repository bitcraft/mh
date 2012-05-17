from errors import *
try:    import cPickle as pickle
except: import pickle as pickle
import zlib

def EncodeData(data,compress):
    data = pickle.dumps(data)
    if compress != False:
        data = zlib.compress(data,compress)
    length = str(len(data))
    length = ("0"*(8-len(length)))+length
    return length,data
def DecodeData(data):
    try:data = pickle.loads(data)
    except:data = pickle.loads(zlib.decompress(data))
    return data
def SendData(sock,data,compress,includelength=False,address=None):
    length,data = EncodeData(data,compress)
    if includelength: data = length + data
    if len(data) > 1024: print "Warning: packets are big."
    try:
        if address != None:
            sock.sendto(data,address)
        else:
            sock.send(data)
    except:
        sock.close()
        raise SocketError("Connection is broken; data could not be sent!")
def ReceiveData(sock):
    try:
        length = int(sock.recv(8))
        data = sock.recv(length)
    except:
        sock.close()
        raise SocketError("Connection is broken; data could not be received!")
    data = DecodeData(data)
    return data
def ReceiveDataUDP(sock,size=1024):
    try:
        data, address = sock.recvfrom(size)
    except:
        sock.close()
        raise SocketError("Connection is broken; data could not be received!")
    data = DecodeData(data)
    return data, address
