from socket import *
from select import select
import sys
import time
import pickle

import argparse
from my_log import log
from errors_list import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
import threading
from common_tools import send_message, get_message
import logging

from chatBase import ChatBaseClass
from meta import Documented

MY_ACCOUNT_NAME = "Nikolay"
MAX_MSG_LEN = 1024

logger = logging.getLogger('app.client')


class ChatClient(ChatBaseClass, Documented):
    def __init__(self, name, addr, port):
        super().__init__(name, addr, port)
        self.logger = logging.getLogger('app.client')
        self.start_fl = False
        # try:
        self.init_socket(addr, port)
        # except:
        #     self.soc_addr = None
        #     self.soc_port = None
        #     self.soc = None
        #     self.logger.info(f"Не удалось запустить сервер. Адрес: {addr}, порт: {port}")
        self.rec_thr = threading.Thread(target=self.msg_read_loop)
        self.rec_thr.daemon = True
        self.send_thr = threading.Thread(target=self.msg_write_loop)
        self.send_thr.daemon = True


    @staticmethod
    def print_help_msg():
        print("Список команд:")
        print("help-- вывести список команд")
        print("msg-- текстовое сообщение")
        print("msg_chat-- сообщение в общий чат")
        print("join_chat-- присоединиться к беседе")
        print("leave_chat-- покинуть беседу")
        print("cr_chat-- создать беседу")
        print("del_chat-- удалить беседу")
        print("exit")

    # @log
    def form_user_user_text_msg(self, recipient, msg_text):
        """"Формируем сообщение с текстом 'msg_text' для пользователя, указанного в 'recipient'
        """
        return {
            "action": "msg",
            "time": time.time(),
            "to": recipient,
            "from": self.name,
            "message": msg_text
        }

    # @log
    def form_user_chat_text_msg(self, recipient, msg_text):
        """"Формируем сообщение с текстом 'msg_text' для беседы, указанного в 'recipient'
                """
        return {
            "action": "msg",
            "time": time.time(),
            "to": "#" + recipient,
            "from": self.name,
            "message": msg_text
        }

    # @log
    def form_join_chat_msg(self, recipient):
        """"Присоединиться к беседе 'recipient', пока не используется
        """
        return {
            "action": "join",
            "time": time.time(),
            "room": "#" + recipient
        }

    # @log
    def form_leave_chat_msg(self, recipient):
        """"Покинуть беседу 'recipient', пока не используется
                """
        return {
            "action": "leave",
            "time": time.time(),
            "room": "#" + recipient
        }

    # @log
    def form_presence_msg(self):
        """"Сформировать presence сообщение
                        """
        return {
            "action": "presence",
            "time": time.time(),
            "user": {
                "account_name": self.name
            }
        }

    # @log
    def form_exit_msg(self):
        """"Сформировать сообщение для выхода из приложения
       """
        return {
            "action": "exit",
            "time": time.time(),
            "account_name": self.name
        }

    def proc_serv_ans(self, msg_data):
        """"Разбор ответного сообщения от сервера
               """
        if "response" in msg_data:
            if msg_data["response"] == 200:
                print('Получен ответ от сервера!')
                return '200 : OK'
            elif msg_data["response"] == 400:
                raise ServerError(f'400 : {msg_data["error"]}')
        raise ReqFieldMissingError("response")

    def init_socket(self, soc_addr, soc_port):
        """"Инициализация сокета
                       """
        try:
            self.soc_addr = soc_addr
            self.soc_port = soc_port
            self.soc = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
            self.soc.connect((self.soc_addr, self.soc_port))  # Соединиться с сервером
            self.send_message(self.soc, self.form_presence_msg())
            print(f"Сокет: {self.soc}")
            serv_answ = self.proc_serv_ans(self.get_message(self.soc))
            print(f'Установлено соединение с сервером, получен ответ: {serv_answ}')
            self.start_fl = True

        except pickle.PicklingError:
            self.logger.error('Не удалось декодировать полученное сообщение.')
            exit(1)
        except ServerError as error:
            self.logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            exit(1)
        except ReqFieldMissingError as missing_error:
            self.logger.error(f'Недопустимый ответ сервера. Отсутствует поле {missing_error.missing_field}')
            exit(1)
        except (ConnectionRefusedError, ConnectionError):
            self.logger.critical(f'Не удалось подключиться к серверу {soc_addr}:{soc_port}.')
            exit(1)
        else:
            self.start_fl = True
            self.print_help_msg()

    def start_read_msg_thr(self):
        """"Старт потока, отвечающего за прием сообщений
        """
        # Запускаем поток на пием сообщений
        self.rec_thr.start()
        self.logger.debug('Запущен поток на прием сообщений')

    def start_send_msg_thr(self):
        """"Старт потока, отвечающего за отправку сообщений
        """
        # Запускаем поток на отправку сообщений.
        self.send_thr.start()
        self.logger.debug('Запущен поток на передачу сообщений')

    def watch_dog_loop(self):
        """"Цикл проверки состояния потоков чтения и передвчи сообщений.
        При закрытии одного из потоков работа программы останавливается.
        """
        # Проверяем состояние потоков, если один из потоков лёг, завершаем программу
        while True:
            time.sleep(1)
            if self.rec_thr.is_alive() and self.send_thr.is_alive():
                continue
            break

    def msg_read_loop(self):
        """"Цикл чтения сообщений.
        """
        while True:
            try:
                print(f"Сокет: {self.soc}")
                inp_message = self.get_message(self.soc)
                print(f"Получено сообщение {inp_message}")
                if 'action' in inp_message and inp_message['action'] == 'msg' and 'from' in inp_message and 'to' in inp_message \
                        and 'message' in inp_message and inp_message['to'] == self.name:
                    print(f'\nПолучено сообщение от пользователя {inp_message["from"]}:\n{inp_message["message"]}')
                    logger.info(f'Получено сообщение от пользователя {inp_message["from"]}:\n{inp_message["message"]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {inp_message}')
            except IncorrectDataRecivedError:
                logger.error(f'Ошибка декодирования сообщения.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
                logger.critical(f'Потеряно соединение с сервером.')
                break
            except:
                break

    def msg_write_loop(self):
        """"Цикл записи сообщений
        """
        while True:
            cmd_type = input('Ведите команду: :\n')
            if cmd_type == 'msg':
                msg_to = input('Введите имя пользователя:\n')
                msg_text = input('Введите текст сообщения:\n')
                self.send_message(self.soc, self.form_user_user_text_msg(msg_to, msg_text))
            elif cmd_type == 'msg_chat':
                msg_to = input('Введите имя беседы:\n')
                msg_text = input('Введите текст сообщения:\n')
                send_message(self.soc, self.form_user_chat_text_msg(msg_to, msg_text))
            elif cmd_type == 'join_chat':
                chat_name = input('Введите имя беседы:\n')
                send_message(self.soc, self.form_join_chat_msg(chat_name))
            elif cmd_type == 'leave_chat':
                chat_name = input('Введите имя беседы:\n')
                send_message(self.soc, self.form_leave_chat_msg(chat_name))
            elif cmd_type == 'exit':
                send_message(self.soc, self.form_exit_msg())
                time.sleep(0.5)
                break
            elif cmd_type == 'help':
                self.print_help_msg()
            else:
                print("Некорректный ввод, попробуйте еще раз")
                self.print_help_msg()

    def main_loop(self):
        """"Основной цикл клиентского приложения
        """
        self.start_read_msg_thr()
        self.start_send_msg_thr()
        self.watch_dog_loop()





