import socket, time, sys
from multiprocessing import Process

BUFFER_SIZE = 1024
HOST = 'localhost'

def get_remote_ip(host):
    print(f'Getting TP for {host}')
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()

    print(f'IP address of {host} is {remote_ip}')
    return remote_ip

def handle_request(conn, proxy_end):
    send_full_data = conn.recv(BUFFER_SIZE)
    print(f'Sending recieved data {send_full_data} to Google')
    proxy_end.sendall(send_full_data)
    # remember to shut down
    proxy_end.shutdown(socket.SHUT_WR)
    data = proxy_end.recv(BUFFER_SIZE)
    print(f'Sending recieved data {data} to clinet')
    conn.send(data)


def main():
    #

    extern_host = 'www.google.com'
    PORT = 8001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start:
        print("Starting proxy server")
        # allow reused addresses, bindm and set to listening mode
        proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_start.bind((HOST, PORT))
        proxy_start.listen(2)

        while True:
            conn, addr = proxy_start.accept()
            print("Connected by", addr)

            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as proxy_end:
                print("Connecting to Google")
                remote_ip = get_remote_ip(extern_host)
                # connect proxy_end
                proxy_end.connect((remote_ip, PORT))

                p = Process(target=handle_request, args=(conn, proxy_end))
                p.daemon = True
                p.start()
                print("Started process", p)
            conn.close()

if __name__ == '__main__':
    main()

