import argparse
from server_thr import ChatServer
from server_database import ServerStorage

MAX_CONNECTIONS = 5
DEF_DB_FILE = 'server_db.db3'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Client App')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=8080, type=int)

    print(f"Порт: {parser.parse_args().port}")


    db_connection = ServerStorage(DEF_DB_FILE)

    my_server = ChatServer('main_server', parser.parse_args().addr, parser.parse_args().port, MAX_CONNECTIONS, db_connection)
    if my_server.is_started():
        while True:
            command = input('Введите комманду: ')
            if command == 'help':
                ChatServer.print_help()
            elif command == 'exit':
                break
            elif command == 'users':
                for user in sorted(db_connection.users_list()):
                    print(f'Пользователь {user[0]}, последний вход: {user[1]}')
            elif command == 'connected':
                for user in sorted(db_connection.active_users_list()):
                    print(
                        f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
            elif command == 'loghist':
                name = input(
                    'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
                for user in sorted(db_connection.login_history(name)):
                    print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
            else:
                print('Команда не распознана. Список доступных команд:')
                ChatServer.print_help()

