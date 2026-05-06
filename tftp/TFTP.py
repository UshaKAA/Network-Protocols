import socket
import struct


class TFTPServer:
    RRQ, WRQ, DATA, ACK, ERROR = 1, 2, 3, 4, 5

    def __init__(self, port=69):
        """ Port 69 is standard TFTP port"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))

    def start(self):
        """Main server loop"""
        print("TFTP Server listening on port 69...")

        while True:
            # 1. Receive packet (should be RRQ)
            packet, addr = self.sock.recvfrom(1024)
            print(f"Received request from {addr}")

            # 2. Parse the packet to get opcode and filename
            opcode = struct.unpack('!H', packet[:2])[0]

            if opcode == self.RRQ:  # Read Request
                # Parse RRQ to extract filename
                # Remember: RRQ format = [opcode][filename\0][mode\0]
                filename = self.parse_rrq(packet)

                # 3. Handle the request
                self.handle_read_request(filename, addr)
            else:
                print(f"Unsupported opcode: {opcode}")

    def handle_read_request(self, filename, client_addr):
        """Handle TFTP read request"""
        try:
            with open(filename, 'rb') as file:
                print(f"[TFTP] Starting transfer: {filename} to {client_addr}")

                # Initialize
                block_num = 1
                max_trial = 3
                timeout = 2.0

                while True:
                    # Read 512 bytes
                    payload = file.read(512)

                    # Build DATA packet
                    packet = struct.pack('!H', TFTPServer.DATA) + struct.pack('!H', block_num) + payload

                    # Try sending with retries
                    ack_received = False

                    for attempt in range(max_trial):
                        print(f"[TFTP] Sending block {block_num}, attempt {attempt + 1}/{max_trial}")

                        # Send packet (INSIDE the loop!)
                        self.sock.sendto(packet, client_addr)
                        self.sock.settimeout(timeout)

                        try:
                            # Wait for ACK
                            recv_data, _ = self.sock.recvfrom(1024)

                            # Parse ACK (extract values with [0]!)
                            recv_opcode = struct.unpack('!H', recv_data[:2])[0]
                            recv_block = struct.unpack('!H', recv_data[2:4])[0]

                            # Check if correct ACK
                            if recv_opcode == TFTPServer.ACK and recv_block == block_num:
                                ack_received = True
                                print(f"[TFTP] ✓ ACK received for block {block_num}")
                                break  # Exit retry loop

                        except socket.timeout:
                            print(f"[TFTP] Timeout on attempt {attempt + 1}")
                            # Loop continues → will resend

                    # Check if all retries failed
                    if not ack_received:
                        print(f"[TFTP] ✗ Failed to send block {block_num} after {max_trial} attempts")
                        return  # Give up

                    # Success! Move to next block
                    block_num += 1

                    # Check if transfer complete
                    if len(payload) < 512:
                        print(f"[TFTP] ✓ Transfer complete! Sent {block_num} blocks")
                        return

        except FileNotFoundError:
            print(f"[TFTP] ERROR: File not found: {filename}")
            self.send_error(client_addr)

    @staticmethod
    def parse_rrq(packet):
        """
        Parse Read Request packet
        Format: [opcode=1][filename\0][mode\0]

        Returns: filename (string)
        """
        # Skip first 2 bytes (opcode)
        data = packet[2:]

        # Split by null bytes
        parts = data.split(b'\x00')

        # Extract filename (first part)
        filename = parts[0].decode('utf-8')

        # Extract mode (second part) - we should check it's "octet"
        mode = parts[1].decode('utf-8') if len(parts) > 1 else ""

        print(f"Parsed RRQ: filename='{filename}', mode='{mode}'")

        return filename

    def send_error(self, addr):
        # Send TFTP ERROR packet
        packet = struct.pack('!H', TFTPServer.ERROR)
        packet+= struct.pack('!H', 1) # ErrorCode 1= file not found
        packet+= b'File Not Found' + b'\x00'
        self.sock.sendto(packet, addr)
        print(f"[TFTP] Sent ERROR to {addr}: File not found")

if __name__ == '__main__':
    server = TFTPServer(port=69)
    server.start()