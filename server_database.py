from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData,  ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime
import time


SERVER_DB = 'server_db.db3'

#Класс для работы базы данных сервера
class ServerStorage:
    # Сущность таблицы со всеми пользователями (как активными, так и нет)
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    # Сущность таблицы активных пользователей
    class ActiveUsers:
        def __init__(self, user_name, ip_addr, port, login_time):
            self.user_id = user_name
            self.ip_address = ip_addr
            self.port = port
            self.login_time = login_time
            self.id = None

    # Сущность таблицы истории пользователей
    class LoginHistory:
        def __init__(self, id, ip, port, date):
            self.id = None
            self.user_id = id
            self.user_ip = ip
            self.user_port = port
            self.log_in_date_time = date
            self.log_out_date_time = None

    def __init__(self, db_file=SERVER_DB):
        # Создание БД
        # connect_args = {'check_same_thread':'False'}
        self.db_engine = create_engine('sqlite:///' + db_file + '?check_same_thread=False', echo=False, pool_recycle=7200)
        self.db_engine.connect_args = {'check_same_thread':'False'}

        self.metadata = MetaData()

        # Таблица всех пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime))

        # Таблица активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('Users.id'), unique=True, ),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime))

        login_history_table = Table('Login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', ForeignKey('Users.id')),
                                    Column('user_ip', String),
                                    Column('user_port', Integer),
                                    Column('log_in_date_time', DateTime),
                                    Column('log_out_date_time', DateTime))

        self.metadata.create_all(self.db_engine)

        # Связываем сущности в ORM с тадлицами
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)

        # Создаем сессию связи с БД
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

        # Подчистим хвост, оставшийся от предыдущей сессии работы сервера в виде остатков таблицы активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()       # Вносим изменения

    # Регистрация входа пользователя
    def reg_user_login(self, user_name, ip_addr, port):
        # Проверка, не является ли пользователь новым
        start_session_datetime = datetime.datetime.now()
        user_db_data = self.session.query(self.AllUsers).filter_by(name=user_name)

        if user_db_data.count():    # Пользователь уже зарегистрирован
            user = user_db_data.first()
            user.last_login = start_session_datetime
        else:       # Новый пользователь
            user = self.AllUsers(user_name)
            self.session.add(user)
            self.session.commit()
            print(f'Зарегистрирован новый пользователь "{user_name}"')


        # Добавляем юзера в активные
        new_active_user = self.ActiveUsers(user.id, ip_addr, port, start_session_datetime)
        self.session.add(new_active_user)

        print(ip_addr, port)

        # Сохраняем историю входов
        login_history = self.LoginHistory(user.id, ip_addr, port, start_session_datetime)
        self.session.add(login_history)

        # Вносим изменения в БД
        self.session.commit()

    def reg_user_logout(self, user_name):
        user = self.session.query(self.AllUsers).filter_by(name=user_name).first()
        start_session_time = user.last_login
        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(user_id=user.id, log_in_date_time=start_session_time).first().log_out_date_time = datetime.datetime.now()
        self.session.commit()

    # Вывести список пользователей
    def users_list(self):
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()      # Список кортежей

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        # Возвращаем список кортежей
        return query.all()

    # Вывести историю входов
    def login_history(self, cur_user_name=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.log_in_date_time,
                                   self.LoginHistory.log_out_date_time,
                                   self.LoginHistory.user_ip,
                                   self.LoginHistory.user_port
                                   ).join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if cur_user_name:
            query = query.filter(self.AllUsers.name == cur_user_name)
        return query.all()



# Отладка
# if __name__ == '__main__':
#     server_db = ServerStorage()
#     # выполняем 'подключение' пользователя
#     server_db.reg_user_login('user_1', '192.168.1.1', 8888)
#     server_db.reg_user_login('user_2', '192.168.1.2', 7777)
#     server_db.reg_user_login('user_3', '192.168.1.3', 5555)
#     # выводим список кортежей - активных пользователей
#     print(server_db.active_users_list())
#     time.sleep(2)
#
#     # выполянем 'отключение' пользователя
#     server_db.reg_user_logout('user_1')
#     print(server_db.active_users_list())
#     time.sleep(1)
#     # выполянем 'отключение' пользователя
#     server_db.reg_user_logout('user_2')
#     time.sleep(1)
#     # выполянем 'отключение' пользователя
#     server_db.reg_user_logout('user_3')
#     # выводим список активных пользователей
#     print(server_db.active_users_list())
#     # запрашиваем историю входов по пользователю
#     server_db.login_history('user_2')
#     # выводим список известных пользователей
#     print(server_db.users_list())
#     print(server_db.login_history())





