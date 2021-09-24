import subprocess

if __name__ == '__main__':
    addr = 'localhost'
    port = '8080'
    p = subprocess.Popen(['python', 'server.py', '-a', addr, '-p', port], creationflags=subprocess.CREATE_NEW_CONSOLE)
    p = subprocess.Popen(['python', 'read_write_client.py', '-a', addr, '-p', port, '-t', 'w'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    p = subprocess.Popen(['python', 'read_write_client.py', '-a', addr, '-p', port, '-t', 'r'], creationflags=subprocess.CREATE_NEW_CONSOLE)
