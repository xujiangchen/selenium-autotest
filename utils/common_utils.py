import socket


def get_host_ip_address():
    try:
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_connection.connect(('8.8.8.8', 80))
        addr, _ = socket_connection.getsockname()
        socket_connection.close()
        return addr
    except socket.error:
        return "127.0.0.1"
