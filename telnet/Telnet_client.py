import socket, time
from TCP_segment_Telnet import TCPSegment

class TelnetClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        # TODO: Create the socket HERE (not in send_bytes).
        # We want one socket for the whole life of the object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # TODO: Set socket timeout (e.g., 2 seconds)
        self.sock.settimeout(2.0)
        # --- STATE VARIABLES ---
        self.seq = 100            # Track our Sequence Number
        self.remote_window = 1024 # Track Server's Available Space (Start full)

    def send_bytes(self, message):
        print(f"Preparing to send: {len(message)} bytes")

        # --- STEP 1: FLOW CONTROL CHECK (The Stop Sign) ---
        # Before we do anything, check if self.remote_window is 0.
        # If it is 0:
        #    Loop or Sleep until it's not 0.
        #    (For this exercise, just print "Window Closed", sleep 3s, and break the wait loop to try sending)
        while self.remote_window == 0:
            print("[Flow Control] Window is 0. Server is busy. Waiting 3s...")
            time.sleep(3.0)
            break

        # --- STEP 2: PREPARE PACKET ---
        # TODO: Create TCPSegment using self.seq and the message
        segment = TCPSegment(self.seq, 0, 1024, 1, message)
        # TODO: Convert to bytes
        segment_bytes = TCPSegment.to_bytes(segment)

        # --- STEP 3: RELIABILITY LOOP (Stop-and-Wait) ---
        while True:
            try:
                # TODO: Send data
                self.sock.sendto(segment_bytes, (self.server_ip, self.server_port))
                # TODO: Wait for Receive (recvfrom)
                recv_bytes, addr = self.sock.recvfrom(1024)
                # TODO: Convert response to TCPSegment
                recv_segment = TCPSegment.from_bytes(recv_bytes)

                # --- UPDATE WINDOW STATE ---
                # TODO: Update self.remote_window with the value from the received segment
                self.remote_window = recv_segment.window
                # Print the new window size so we can see it happening
                print(f"Server Window is now: {self.remote_window}")

                # --- CHECK ACK ---
                # TODO: Check if ack_num is correct (self.seq + len(message))
                excepted_ack = self.seq + len(message)
                # IF correct:
                #    Update self.seq (so next packet uses new number)
                #    Break loop (Success)
                if recv_segment.ack_num == excepted_ack:
                    print(f"Success! ACKed {recv_segment.ack_num}")
                    self.seq = excepted_ack # Update SEQ for next message
                    break
                else:
                    print("Wrong ACK")

            except socket.timeout:
                print("Timeout! Retrying...")
            except Exception as e:
                print(e)
                break

    def close(self):
        # TODO: Close socket
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    cli = TelnetClient('127.0.0.1', 25000)

    # Scenario: Server has 4 bytes buffer.
    cli.send_bytes("Hi")  # 2 bytes. Server Window should drop to 2.
    cli.send_bytes("Yo")  # 2 bytes. Server Window should drop to 0.
    cli.send_bytes("Go")  # Client should PAUSE here because Window is 0.
    cli.close()