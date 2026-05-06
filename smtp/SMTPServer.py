import socket

class SMTPServer:
    def __init__(self, host='127.0.0.1', port=25):
        self.host = host
        self.port = port
        self.sock = None 

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

        # Listen 
        self.sock.listen()
        print(f'[SMTP] Listen: {self.host}:{self.port}')

        while True:
            try:
                """ Accept client connection, and returns a new socket for that client"""
                client_socket, client_address = self.sock.accept()
                print(f'Client connected from: {client_socket}')

                # Handle connection for single client
                self.handle_client(client_socket,client_address)

            except Exception as e:
                print(f'Interrupt {e}')
                break

        self.stop()

    @staticmethod
    def handle_client(client_socket, addr):
        client_socket.send(b'220 Welcome to SMTP Server\r\n')
        # wait for response
        while True:
            try:
                command = client_socket.recv(1024)
                command = command.decode('utf-8').strip()
                print(f'Received: {command}')

                # Parse the command - get the first word (the actual command)
                cmd_parts = command.split()
                if not cmd_parts:
                    continue

                smtp_command = cmd_parts[0].upper()

                if smtp_command == 'HELO':
                    # HELO command format: HELO <domain>
                    # Response: 250 Hello <domain>, pleased to meet you
                    if len(cmd_parts) > 1:
                        domain = cmd_parts[1]
                        client_socket.send(f'250 Hello {domain}, pleased to meet you\r\n'.encode('utf-8'))
                    else:
                        client_socket.send(b'501 Syntax: HELO <domain>\r\n')

                elif smtp_command == 'MAIL':
                    # MAIL FROM command format: MAIL FROM:<sender@example.com>
                    # Response: 250 OK
                    if len(cmd_parts) >= 2 and cmd_parts[1].startswith('FROM:'):
                        sender = cmd_parts[1][5:]  # Remove 'FROM:'
                        client_socket.send(f'250 OK, sender is {sender}\r\n'.encode('utf-8'))
                    else:
                        client_socket.send(b'501 Syntax: MAIL FROM:<address>\r\n')

                elif smtp_command == 'RCPT':
                    # RCPT TO command format: RCPT TO:<recipient@example.com>
                    # Response: 250 OK
                    if len(cmd_parts) >= 2 and cmd_parts[1].startswith('TO:'):
                        recipient = cmd_parts[1][3:]  # Remove 'TO:'
                        client_socket.send(f'250 OK, recipient is {recipient}\r\n'.encode('utf-8'))
                    else:
                        client_socket.send(b'501 Syntax: RCPT TO:<address>\r\n')

                elif smtp_command == 'DATA':
                    # DATA command - start accepting email body
                    # Response: 354 End data with <CRLF>.<CRLF>
                    client_socket.send(b'354 End data with <CRLF>.<CRLF>\r\n')
                    # In a real implementation, you'd collect the email body here
                    # For simplicity, we'll just acknowledge
                    email_data = []
                    while True:
                        line = client_socket.recv(1024).decode('utf-8').strip()
                        if line == '.':
                            break
                        email_data.append(line)
                    client_socket.send(b'250 OK, message queued for delivery\r\n')

                elif smtp_command == 'QUIT':
                    # QUIT command - end the session
                    client_socket.send(b'221 Goodbye\r\n')
                    break  # Exit the while loop

                else:
                    # Unknown command
                    client_socket.send(b'502 Command not implemented\r\n')

            except KeyboardInterrupt as e:
                print(f'\nInterrupt: {e}')
                break
        client_socket.close()

    def stop(self):
        self.sock.close()
        print(f'\nServer Shutting down')

