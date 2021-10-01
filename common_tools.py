
from errors_list import IncorrectDataRecivedError, NonDictInputError
import sys
sys.path.append('../')
from my_log import log
import pickle


# Утилита приёма и декодирования сообщения
# принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
#@log
def get_message(client, max_msg_len):
    encoded_response = client.recv(max_msg_len)
    if isinstance(encoded_response, bytes):
        response = pickle.loads(encoded_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


# Утилита кодирования и отправки сообщения
# принимает словарь и отправляет его
#@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise NonDictInputError
    encoded_message = pickle.dumps(message)
    sock.send(encoded_message)
