import argparse
from server import ChatServer

MAX_CONNECTIONS = 5

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Client App')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=-8080, type=int)

    print(f"Порт: {parser.parse_args().port}")
    my_server = ChatServer('main_server', parser.parse_args().addr, parser.parse_args().port, MAX_CONNECTIONS)
    if my_server.is_started():
        my_server.main_loop()

