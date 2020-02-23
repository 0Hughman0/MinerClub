import socket
import threading

from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler, FTPHandler
from pyftpdlib.ioloop import IOLoop

import paramiko
from paramiko.server import AUTH_FAILED, AUTH_SUCCESSFUL
from paramiko.rsakey import RSAKey
from sftpserver import StubServer, StubSFTPServer


class TestServer:

    def start(self):
        self.thread.start()

    def __enter__(self):
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class TestFTPServer(TestServer):

    def __init__(self, username, password, address, port, use_ssl, top_dir):
        self.ioloop = IOLoop()

        self.thread = threading.Thread(target=run_ftp_server, args=[username, password, address, port, use_ssl, top_dir, self.ioloop])

    def stop(self):
        self.ioloop.close()
        self.thread.join()


class TestSFTPServer(TestServer):
    def __init__(self, username, password, address, port, top_dir):
        self.event = threading.Event()

        self.thread = threading.Thread(target=run_sftp_server, args=[username, password, address, port, top_dir, self.event])

    def stop(self):
        self.event.set()
        self.thread.join()


def run_ftp_server(username, password, address, port, use_ssl, top_dir, loop):
    authorizer = DummyAuthorizer()
    authorizer.add_user(username,
                        password,
                        top_dir,
                        perm='elradfmwMT')

    if use_ssl:
        handler = TLS_FTPHandler
        handler.certfile = 'tests/dummycert.pem'
        handler.tls_control_required = True
        handler.tls_data_required = True
    else:
        handler = FTPHandler

    handler.authorizer = authorizer
    server = FTPServer((address, port), handler, ioloop=loop)

    try:
        server.serve_forever(timeout=2)
    finally:
        server.close_all()


def run_sftp_server(username, password, address, port, top_dir, event):
    # adapted from https://github.com/rspivak/sftpserver/blob/master/src/sftpserver/__init__.py

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.bind((address,
                        port))
    server_socket.listen(10)
    server_socket.settimeout(0.5)

    class PasswordAuthServer(StubServer):
        def check_auth_password(self, u, p):
            if u == username and \
               p == password:
                return AUTH_SUCCESSFUL
            return AUTH_FAILED

    class UnrootedSFTPServer(StubSFTPServer):
        ROOT = top_dir

    while not event.is_set():
        try:
            conn, addr = server_socket.accept()  # will block until a connection made, or timeout!
        except socket.timeout:
            continue # in which case wait again for a connection.

        transport = paramiko.Transport(conn)
        transport.add_server_key(RSAKey.generate(1024))
        transport.set_subsystem_handler(
            'sftp', paramiko.SFTPServer, UnrootedSFTPServer)

        server = PasswordAuthServer()
        transport.start_server(server=server)

        channel = transport.accept()

    server_socket.close()
