from errors_list import IncorrectDataRecivedError, NonDictInputError
import sys
sys.path.append('../')
from my_log import log
import pickle
from discriptors import ServerVerifier

DEF_MAX_MSG_LEN = 1024

class ChatBaseClass():
    soc_port = ServerVerifier('server')

    def __init__(self, name, addr, port):
        self.name = name
        self.soc_addr = addr
        self.soc_port = port
        self.sock = None
        self.max_msg_len = DEF_MAX_MSG_LEN

    def get_message(self, cl_sock):
        encoded_response = cl_sock.recv(self.max_msg_len)
        if isinstance(encoded_response, bytes):
            response = pickle.loads(encoded_response)
            if isinstance(response, dict):
                return response
            else:
                raise IncorrectDataRecivedError
        else:
            raise IncorrectDataRecivedError

    def send_message(self, cl_sock, message):
        if not isinstance(message, dict):
            raise NonDictInputError
        encoded_message = pickle.dumps(message)
        cl_sock.send(encoded_message)
