import subprocess

if __name__ == '__main__':
    addr = 'localhost'
    port = '8080'

    try:
        count_r_cl = int(input('Введите количество запускаемых клиентов на чтение:\n'))
        count_wr_cl = int(input('Введите количество запускаемых клиентов на отправку сообщений:\n'))
        p = subprocess.Popen(['python', 'server.py', '-a', addr, '-p', port],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        for _ in range(count_r_cl):
            p = subprocess.Popen(['python', 'read_write_client.py', '-a', addr, '-p', port, '-t', 'r'],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
        for _ in range(count_wr_cl):
            p = subprocess.Popen(['python', 'read_write_client.py', '-a', addr, '-p', port, '-t', 'w'],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
    except:
        print('Некорректный ввод данных!')

