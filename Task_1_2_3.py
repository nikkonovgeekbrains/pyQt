import subprocess
import ipaddress
from tabulate import tabulate


#Task 1
def host_ping(inp_adr_list):
    for adr in inp_adr_list:
        # p = subprocess.Popen(['ping', adr], creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=subprocess.PIPE)
        p = subprocess.Popen(['ping', str(adr)], stdout=subprocess.PIPE)
        outp_stream = p.stdout.read()
        #print(outp_stream.decode('cp866'))
        split_str = outp_stream.decode('cp866').split()
        #print(split_str)

        if 'отправлено' in split_str:
            pac_count = int(split_str[split_str.index('отправлено') + 2].replace(',', ''))
            rec_pac_count = int(split_str[split_str.index('получено') + 2].replace(',', ''))
            lost_pac_count = int(split_str[split_str.index('потеряно') + 2].replace(',', ''))

            #print(pac_count, rec_pac_count, lost_pac_count)
            if rec_pac_count > 0:
                print(f'Узел {adr} доступен. Потеряно {lost_pac_count} из {pac_count} пакетов')
                return True
            else:
                print(f'Узел {adr} не отвечает. Потеряно {lost_pac_count} пакеторв из {pac_count}')
                return False
        else:
            print(f'Узел {adr} не найден')
            return False

#Task2
def host_range_ping(first_adr, last_adr):
    if ipaddress.ip_interface(str(first_adr) + '/24').network == ipaddress.ip_interface(str(last_adr) + '/24').network:
        if int(last_adr) >= int(first_adr):
            adr_iter = range(int(first_adr), int(last_adr)+1)
        else:
            adr_iter = range(int(last_adr), int(first_adr) + 1)

        av_adr_list = []
        unav_adr_list = []
        for adr in adr_iter:
            #print(ipaddress.ip_address(adr))
            if host_ping([ipaddress.ip_address(adr)]):
                av_adr_list.append(str(ipaddress.ip_address(adr)))
            else:
                unav_adr_list.append(str(ipaddress.ip_address(adr)))

        if len(av_adr_list):
            print(f'Список доступных адресов указанного диапазона: {av_adr_list}')
        else:
            print('В указанном диапазоне нет доступных адресов')
        return {'Reachable': av_adr_list, 'Unreachable': unav_adr_list}
    else:
        print('Некорректный ввод данных. Введите адрема из одной 24 подсети.')
        return -1

#Task3
def host_range_ping_tab(first_adr, last_adr):
    adr_data = host_range_ping(first_adr, last_adr)
    print(tabulate(adr_data, headers='keys', tablefmt="pipe"))




if __name__ == '__main__':
    #Task 1
    adr_list = [ipaddress.ip_address('127.0.0.1'), ipaddress.ip_address('192.168.44.121'), 'yandex.ru', 'yandexhbbfgfd.ru']
    host_ping(adr_list)

    #Task2
    first_inp_adr = ipaddress.ip_address('192.168.44.123')
    last_inp_adr = ipaddress.ip_address('192.168.44.120')
    host_range_ping(first_inp_adr, last_inp_adr)

    #Task3
    host_range_ping_tab(first_inp_adr, last_inp_adr)


