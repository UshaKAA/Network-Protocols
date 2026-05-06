import struct
import socket
def send_rrq(filename, server_ip='127.0.0.1', server_port=69, save_as=None):
    """Send Read Request and receive file"""

    if save_as is None:
        save_as = f"downloaded_{filename}"

    # Create RRQ packet
    packet = struct.pack('!H', 1)  # Opcode = 1 (RRQ)
    packet += filename.encode() + b'\x00'
    packet += b'octet\x00'

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send RRQ
    sock.sendto(packet, (server_ip, server_port))
    print(f"Sent RRQ for '{filename}' to {server_ip}:{server_port}")

    # Open file to write
    with open(save_as, 'wb') as file:
        total_bytes = 0

        while True:
            # Receive DATA packet
            data, addr = sock.recvfrom(1024)

            # Parse DATA packet
            opcode = struct.unpack('!H', data[:2])[0]
            block_num = struct.unpack('!H', data[2:4])[0]
            payload = data[4:]

            print(f"Received block {block_num}, size {len(payload)} bytes")

            if opcode == 3:  # DATA
                # Write to file
                file.write(payload)
                total_bytes += len(payload)

                # Send ACK
                ack = struct.pack('!H', 4) + struct.pack('!H', block_num)
                sock.sendto(ack, addr)
                print(f"Sent ACK for block {block_num}")

                # Check if last block
                if len(payload) < 512:
                    print(f"\n✓ Transfer complete! Received {total_bytes} bytes")
                    print(f"✓ Saved as: {save_as}")
                    break

            elif opcode == 5:  # ERROR
                error_code = struct.unpack('!H', data[2:4])[0]
                error_msg = data[4:].decode('utf-8').rstrip('\x00')
                print(f"✗ ERROR {error_code}: {error_msg}")
                sock.close()
                return False

    sock.close()
    return True


# Test it
if __name__ == '__main__':
    success = send_rrq('challenge.txt', save_as='received_test.txt')

    if success:
        # Read and display the downloaded file
        with open('received_test.txt', 'r') as f:
            print(f"\nDownloaded file content:")
            f.read()
    else:
        print("Failed to download file")