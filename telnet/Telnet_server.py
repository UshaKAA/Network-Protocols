import socket, time
from Telnet import TCPSegment

class TelnetServer:
    def __init__(self, ip='127.0.0.1', port=25000):
        self.ip = ip
        self.port = port
        self.sock = None
        # TODO: Define a maximum buffer capacity (e.g., 4 bytes for testing)
        self.buffer_capacity = 4
        # TODO: Define a variable for 'current_free_space' starting at max capacity
        self.current_free_space = 4

    def start(self):
        # TODO: Create UDP socket and Bind
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((self.ip, self.port))
        except Exception as e:
            print(f'Error binding: {e}')
        print(f"Server listening {self.ip}:{self.port}...")
        while True:
            try:
                # TODO: Receive raw bytes and address
                data, addr = self.sock.recvfrom(1024)
                # TODO: Convert raw bytes to TCPSegment object
                segment = TCPSegment.from_bytes(data)
                payload_len = len(segment.data)

                # --- FLOW CONTROL CHECK: ACK Segment---
                # TODO: Check if payload_len is greater than current_free_space
                # IF it is too big:
                #    Print "Dropping packet, buffer full"
                #    Continue (skip the rest of the loop, effectively dropping the packet)
                if self.current_free_space < payload_len:
                    print("Dropping packet, buffer full")
                    continue

                # --- PROCESS DATA | Accept Data---
                # TODO: Decrease current_free_space by payload_len
                next_window = self.current_free_space - payload_len
                self.current_free_space = next_window if next_window > 0 else 0
                print(f"Received: {segment.data}. Window remaining: {self.current_free_space}")

                # --- PREPARE ACK | Reply---
                # TODO: Calculate Next Expected Byte (SEQ + LEN(DATA))
                ack_response: int = segment.seq + payload_len
                # TODO: Create response TCPSegment.
                # CRITICAL: Set the 'window' field in the header to 'self.current_free_space'!
                response_seg = TCPSegment(500, ack_response, self.current_free_space, 16, "")
                # TODO: Send the segment back
                self.sock.sendto(response_seg.to_bytes(), addr)

                # --- SIMULATE APPLICATION READING BUFFER ---
                # If buffer is empty (0), we need to 'read' it to make space again.
                if self.current_free_space == 0:
                    print("Buffer full! Application processing data...")
                    # TODO: Sleep for 5 seconds (simulate slow CPU)
                    time.sleep(5)
                    # TODO: Reset current_free_space back to max capacity
                    self.current_free_space = self.buffer_capacity
                    print("Buffer cleared! Window Open.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5.0)

        if self.sock:
            self.sock.close()
            print('Server socket close')

if __name__ == "__main__":
    serv = TelnetServer()
    serv.start()