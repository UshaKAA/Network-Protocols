import socket
import sys
import time

IP='127.0.0.1'
BUFFER_SIZE=1024
TRAP_PORT=162
class SNMPAgent:
    """
    Represents the Network Device (Router/Switch)
    Listens for incoming UDP SNMP requests.
    """
    def __init__(self, ip ='127.0.0.1', port=16100, community='public'):
        self.ip = ip 
        self.port = port
        self.community = community      # Password
        self.sock = None 
        self.trap = None    

        # Create your MIB (Dictionary)
        # '1.3.6.1.2.1.1.5' -> 'Router_Hostname'
        self.mib = {
            '1.3.6.1.2.1.1.1': 'PyRouter System Description',
            '1.3.6.1.2.1.1.5': 'Router_Hostname'
        }


    def start_service(self):
        print(f"[*] Agent Starting on {self.ip}:{self.port}...")
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind to this IP:PORT
        try:
            self.sock.bind((self.ip, self.port))
        except Exception as e:
            print(f"Error binding: {e}")
            return 
        print("[*] Agent is listening for SNMP Requests (UDP)...")

        # Simple loop to keep listening
        try:
            while True:
                # Listening for incoming request
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                message = data.decode('utf-8')
                print(f"DEBUG: Raw Packet Received: {len(message)}")

                if self.verify_community(message):
                    print("Access Granted: Processing OID...")
                    self.handle_request(message, addr)
                else:
                    print("Authentication Failed - Drop Packet")

        except KeyboardInterrupt:
            print('\nStopping Agent')
            self.sock.close()


    def verify_community(self, message):
        parts = message.split('|')
        if parts[0] == self.community:
            return True
        return False


    def handle_request(self, message, client_addr):
        # Updated Format: "public|COMMAND|OID|VALUE"
        try:
            parts = message.split('|')
            # Handle cases where value might be missing (for backward compatibility or simple GETs)
            community = parts[0]
            command = parts[1]
            oid = parts[2]
            value = parts[3] if len(parts) > 3 else None
        except IndexError:
            print("[-] Malformed Packet")
            return

        print(f"[*] Processing {command} for OID: {oid}")

        if command == 'GET':
            if oid in self.mib:
                self.sock.sendto(self.mib[oid].encode('utf-8'), client_addr)
            else:
                self.sock.sendto(b"Error: OID NOT FOUND", client_addr)

        elif command == 'SET':
            # Security: In real SNMP, we check if community == 'private' for writes.
            # 1. Update self.mib[oid] with the new 'value'.
            # 2. Send a confirmation back (usually the new value).
            if community == 'private' and value != None:
                self.mib[oid] = value
                self.sock.sendto(f'{oid} = {value}'.encode(), client_addr)

        elif command == 'GETNEXT':
            # 3. Return the value of the *next* OID in the list.
            # 4. If the requested OID is the last one, return "END OF MIB".
            sorted_keys = sorted(self.mib.keys())
            if oid in sorted_keys:
                i = sorted_keys.index(oid)
                if i == len(sorted_keys)-1:
                    self.sock.sendto(b'END OF MIB', client_addr)
                else:
                    next_oid = sorted_keys[i+1]
                    val = self.mib[next_oid]
                    self.sock.sendto(f"{next_oid} = {val}".encode(), client_addr)
            else:
                self.sock.sendto(b"OID NOT FOUND", client_addr)

    def send_trap(self, manager_ip, manager_port, oid, message):
        """
        Sends a Trap (Fire and Forget)
        """
        print(f"[!] Sending TRAP to {manager_ip}:{manager_port}")
        trap_msg = f"{self.community}|TRAP|{oid}|{message}"
        
        # 1. Create a TEMPORARY socket just for this message
        # We do NOT bind. We let the OS pick a random source port.
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            temp_sock.sendto(trap_msg.encode('utf-8'), (manager_ip, manager_port))
            print("    -> Trap sent.")
        except Exception as e:
            print(f"    -> Error sending trap: {e}")
        finally:
            temp_sock.close()

    def send_inform(self, manager_ip, manager_port, oid, message):
        """
        Sends an Inform (Reliable - Waits for ACK)
        """
        print(f"[!] Sending INFORM to {manager_ip}:{manager_port}")
        inform_msg = f"{self.community}|INFORM|{oid}|{message}"
        
        # 1. Create a socket
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.settimeout(3) # Wait 3 seconds for ACK
        
        # 2. Send
        try:
            temp_sock.sendto(inform_msg.encode('utf-8'), (manager_ip, manager_port))
            
            # 3. Wait for ACK on the SAME socket
            data, _ = temp_sock.recvfrom(1024)
            response = data.decode('utf-8')
            
            if "ACK" in response:
                print("    -> Manager Acknowledged (ACK Received).")
            else:
                print(f"    -> Unexpected response: {response}")
                
        except socket.timeout:
            print("    -> [X] No ACK received. Inform Failed.")
        finally:
            temp_sock.close()

            

class SNMPManager:
    """
    Represents the NMS (Network Management System)
    Sends UDP requests.
    """
    def __init__(self, ip=IP, port=16100):
        self.ip = ip
        self.port = port 


    def send_request(self, community, command, oid, value=''):
        # Format Community|command|oid
        formatted_msg = f"{community}|{command}|{oid}|{value}"
        print(f"[*] Manager sending '{formatted_msg}' to {self.ip}:{self.port}")
        
        # Create a UDP Socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        client_sock.sendto(formatted_msg.encode('utf-8'), (self.ip, self.port))

        # TODO: 3. Wait for the response!
        # Set a timeout so we don't hang forever if the packet is lost (UDP is unreliable!)
        client_sock.settimeout(2) 

        try:
            data, _ = client_sock.recvfrom(BUFFER_SIZE)
            print(f"[*]Agent Respond: {data.decode('utf-8')}")
        except socket.timeout:
            print("[!] Request Timed Out (UDP Packet Lost or Wrong IP)")
        
        finally:
            # Close the socket (UDP is connectionless, so we usually close after sending in simple scripts)
            client_sock.close()
    
    def send_get_next(self, community, oid):
        self.send_request(community, "GETNEXT", oid)

    
    def send_set(self, community, oid, new_value):
        # Call send_request with the arguments
        # private|Set|oid|new_value
        self.send_request(community, "SET", oid, new_value)

    
    def listen_trap(self, listen_port=TRAP_PORT):
        """
        Listens for incoming Traps/Informs
        """
        trap_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        trap_sock.bind((self.ip, listen_port))
        
        print(f"[*] Manager Listening for Traps on {self.ip}:{listen_port}...")
        
        while True:
            
            data, addr = trap_sock.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"[!] TRAP RECEIVED from {addr}: {message}")
            
            # Check if the message contains "|INFORM|".
            if "|INFORM|" in message:
                print(f"[*] Sending ACK to {addr}...")
                trap_sock.sendto(b"ACK", addr)



if __name__ == "__main__":
    role = input("Run as (A)gent, (M)anager, or (T)rapListener? > ").lower()
    
    if role == 'a':
        agent = SNMPAgent()
        # Simulate a choice:
        action = input("Start (S)ervice or Send (T)rap or Send (I)nform? > ").lower()
        if action == 's':
            agent.start_service()
        elif action == 't':
            agent.send_trap('127.0.0.1', 16200, "1.3.6.1.4.1.9.0", "Interface Down")
        elif action == 'i':
            agent.send_inform('127.0.0.1', 16200, "1.3.6.1.4.1.9.0", "Overheating")

    elif role == 'm':
        mgr = SNMPManager()
        mgr.send_request("public", "GET", "1.3.6.1.2.1.1.1")
        
    elif role == 't':
        mgr = SNMPManager()
        mgr.listen_trap()