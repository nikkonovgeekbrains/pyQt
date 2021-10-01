import argparse
from client import ChatClient

MAX_CONNECTIONS = 5

if __name__ == '__main__':
    print("Клиентский модуль сетевого чата")
    parser = argparse.ArgumentParser(description='Client App')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=8080, type=int)
    parser.add_argument('-n', '--name', default=None, type=str)

    cl_adr = (parser.parse_args().addr, parser.parse_args().port)
    cl_name = parser.parse_args().name

    if not cl_name:
        cl_name = input('Введите имя пользователя:')

    my_client = ChatClient(cl_name, parser.parse_args().addr, parser.parse_args().port)
    my_client.main_loop()

