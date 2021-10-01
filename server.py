import json
import time
from socket import *

import argparse
import sys
import pickle
import os
import logging

import log.server_log_config
import logging
import select
from my_log import log
from common_tools import get_message, send_message
from chatBase import ChatBaseClass


MAX_MSG_LEN = 1024

logger = logging.getLogger('app.server')



class ChatServer(ChatBaseClass):

    def __init__(self, name, addr, port, max_connections):
        super().__init__(name, addr, port)
        self.logger = logging.getLogger('app.server')
        self.all_clients = []
        self.msg_buf = []
        self.cl_names = {}
        self.wait = 10
        self.rec_data_cl = []
        self.send_data_cl = []
        self.max_connections = max_connections
        self.start_fl = False       # Флаг успешного старта сервера
        # try:
        self.init_socket(addr, port)
        # except:
            # self.soc_addr = None
            # self.soc_port = None
            # self.soc = None
            # self.logger.info(f"Не удалось запустить сервер. Адрес: {addr}, порт: {port}")

    def init_socket(self, soc_addr, soc_port):
        self.soc_addr = soc_addr
        self.soc_port = soc_port
        self.soc = socket(AF_INET, SOCK_STREAM)
        self.soc.bind((self.soc_addr, self.soc_port))
        self.soc.listen(self.max_connections)
        self.soc.settimeout(0.5)  # Таймаут для операций с сокетом
        self.logger.info(f"Запущен сервер. Адрес: {self.soc_addr}, порт: {self.soc_port}")
        self.start_fl = True

    def is_started(self):
        return self.start_fl

    # @log
    def form_cl_msg(self, input_mes):
        logger.debug(f"json:{input_mes}")
        logger.debug(f"pikle:{pickle.loads(input_mes)}")
        if pickle.loads(input_mes)["action"] == "presence":
            out_pack = pickle.dumps({
                "response": 100,
                # "time": time.ctime(datetime.now().timestamp()),
                "time": time.time(),
                "alert": "Hi, Client!"
            }, )
            logger.info(f"Отправлен пакет {out_pack}")
            return out_pack

    # @log
    def form_probe_msg(self):
        return pickle.dumps({
            "action": "probe",
            "time": time.time()
        }, )

    def form_response_200_msg(self):
        return {"response": 200}

    def form_response_400_msg(self, err_txt):
        return {
            "response": 400,
            "error": err_txt
        }


    def read_requests(self):
        """ Чтение запросов из списка клиентов
            """
        for client in self.rec_data_cl:
            # print(f"cur_client: {client}")
            try:
                msg_data = self.get_message(client)
                # Presence
                print(f"msg_data: {msg_data}")
                if "action" in msg_data and msg_data[
                    "action"] == "presence" and "time" in msg_data and "user" in msg_data:
                    # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.

                    if msg_data["user"]["account_name"] not in self.cl_names.keys():
                        self.cl_names[msg_data["user"]["account_name"]] = client
                        self.send_message(client, self.form_response_200_msg())
                    else:
                        self.send_message(client, self.form_response_400_msg('Имя пользователя уже занято.'))
                        self.all_clients.remove(client)
                        client.close()
                    return

                # Message
                elif "action" in msg_data and msg_data["action"] == "msg" and "to" in msg_data and "time" in msg_data \
                        and "from" in msg_data and "message" in msg_data:
                    self.msg_buf.append(msg_data)
                    return
                # Exit
                elif "action" in msg_data and msg_data["action"] == "exit" and "account_name" in msg_data:
                    # print(f'\n\n\n\n\n\nПользователь {msg_data["account_name"]} отключился!\n\n\n\n\n\n\n')

                    # print(f"Имена: {self.cl_names}")
                    self.all_clients.remove(self.cl_names[msg_data["account_name"]])
                    self.cl_names[msg_data["account_name"]].close()
                    del self.cl_names[msg_data["account_name"]]
                    print(f'Пользователь {msg_data["account_name"]} отключился.')
                    # print(f"Новые имена: {self.cl_names}")
                    return
                # Bad response
                else:
                    self.send_message(client, self.form_response_400_msg('Запрос некорректен.'))
                    return
                # if msg_data:
                #     print(msg_data)
            except:
                find_fl = False
                targ_name = None
                for us_name in self.cl_names:
                    if self.cl_names[us_name] == client:
                        find_fl = True
                        targ_name = us_name
                        print(f'Пользователь {us_name} отключился.')
                if find_fl:
                    del self.cl_names[targ_name]
                else:
                    print('Клиент {} {} отключился'.format(client.fileno(), client.getpeername()))
                self.all_clients.remove(client)

    def proc_messages(self):
        for msg in self.msg_buf:
            try:
                self.proc_tr_msg(msg)
            except:
                logger.info(f'Связь с клиентом с именем {msg["to"]} была потеряна')
                self.all_clients.remove(self.cl_names[msg['to']])
                del self.cl_names[msg['to']]

    def proc_tr_msg(self, msg_data):
        if msg_data["to"] in self.cl_names and self.cl_names[msg_data["to"]] in self.all_clients:
            print("Пробуем переслать сообщение!")
            self.send_message(self.cl_names[msg_data["to"]], msg_data)
            logger.info(f'Отправлено сообщение пользователю {msg_data["to"]} от пользователя {msg_data["from"]}.')
        elif msg_data["to"] in self.cl_names and self.cl_names[msg_data["to"]] not in self.all_clients:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {msg_data["to"]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def clear_msg_buf(self):
        self.msg_buf.clear()

    def main_loop(self):
        while True:
            try:
                conn, addr = self.soc.accept()  # Проверка подключений
            except OSError as e:
                pass
                # print(e)
            else:
                print(f"Получен запрос на соединение от {str(addr)}")
                self.all_clients.append(conn)
                # print(f"all_clients: {self.all_clients}")
            finally:
                self.rec_data_cl = []
                self.send_data_cl = []
                try:
                    self.rec_data_cl, self.send_data_cl, _ = select.select(self.all_clients, self.all_clients, [], self.wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился

                self.read_requests()
                # Если есть сообщения, обрабатываем каждое.
                self.proc_messages()
                self.clear_msg_buf()


