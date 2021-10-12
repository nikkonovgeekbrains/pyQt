import subprocess

if __name__ == '__main__':
    addr = 'localhost'
    port = '8080'
    p = subprocess.Popen(['python', 'runserver.py', '-a', addr, '-p', port], creationflags=subprocess.CREATE_NEW_CONSOLE)
    p = subprocess.Popen(['python', 'runclient.py', '-a', addr, '-p', port], creationflags=subprocess.CREATE_NEW_CONSOLE)
    p = subprocess.Popen(['python', 'runclient.py', '-a', addr, '-p', port], creationflags=subprocess.CREATE_NEW_CONSOLE)
