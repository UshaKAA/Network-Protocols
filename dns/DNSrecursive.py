import time

# CCNA Concept: DNS Record Types
# These are constants we will use to identify the type of data
RECORD_A = "A"         # Maps Hostname -> IPv4
RECORD_AAAA = "AAAA"   # Maps Hostname -> IPv6
RECORD_CNAME = "CNAME" # Maps Hostname -> Alias (Canonical Name)
RECORD_MX = "MX"       # Maps Domain -> Mail Server
RECORD_PTR = "PTR"     # Maps IPv4 -> Hostname (Reverse DNS)


class DNSRecord:

    def __init__(self, name, record_type, value, ttl):
        """
        Initializes a DNS Resource Record.

        Args:
            name (str): The domain name (e.g., 'example.com')
            record_type (str): The type (A, AAAA, CNAME, etc.)
            value (str): The data (IP address or alias name)
        """
        self.name = name
        self.record_type = record_type
        self.value = value
        self.ttl = ttl
        self.create_time = time.time()

    def is_expired(self) -> bool:
        """
        Checks if the current time has passed the creation time + TTL.
        Returns:
            bool: True if expired, False otherwise.
        """
        current_time = time.time()
        if current_time > (self.create_time + self.ttl):
            return True
        return False


    def __str__(self):
        """
        Returns a formatted string representation of the record.
        Example: "google.com (A) -> 142.250.190.46 [TTL: 300]"
        """
        return f"{self.name} ({self.record_type}) -> {self.value} [TTL: {self.ttl}]"


class DNSZone:
    def __init__(self):
        """
        Initializes the DNS Zone File (Database).
        self.records is a dictionary:
            { "domain_name": [List_of_DNSRecord_objects] }
        """
        self.records = {}

    def add_record(self, record):
        """
        Adds a DNSRecord to the zone file.

        Args:
            record (DNSRecord): The record object to add.

          Each domain maps to a list of DNSRecord objects,
          because a domain can have multiple records (e.g., multiple A records, MX, etc.),
          and TTL, record_type, IP, etc. are all properties of each record, not of the domain itself.
        """
        if record.name not in self.records:
            self.records[record.name] = []
        self.records[record.name].append(record)
        print(f"Added record: {record} to the Zone File")

    def resolve(self, name):
        """
        Looks up a domain name with Round Robin rotation.
        Args:
            name (str): The domain to look up.
        Returns:
            list: A list of DNSRecord objects, or empty list if not found.
        """
        records = self.records.get(name, [])
        if records:
            # Round Robin: Move first record to the end
            first_record = records.pop(0)
            records.append(first_record)
        return records

    def reverse_lookup(self, ip_address):
        """
        Performs reverse DNS lookup (IP -> hostname).
        Converts IP to reverse DNS format and looks up PTR records.

        Args:
            ip_address (str): IPv4 address like "192.168.1.1"

        Returns:
            list: A list of DNSRecord objects (PTR records), or empty list if not found.
        """
        # Convert IP to reverse DNS format: 192.168.1.1 -> 1.1.168.192.in-addr.arpa
        octets = ip_address.split('.')
        if len(octets) != 4:
            return []  # Invalid IPv4 address

        reverse_domain = f"{octets[3]}.{octets[2]}.{octets[1]}.{octets[0]}.in-addr.arpa"
        print(f"   -> Reverse lookup: {ip_address} -> {reverse_domain}")

        return self.records.get(reverse_domain, [])


class RecursiveResolver:
    def __init__(self):
        """
        Simulates an ISP DNS Resolver (like 8.8.8.8).
        It has a cache to store results from previous lookups.
        """
        self.cache = {}
        self.round_robin_index = {}  # For round-robin load balancing

    def query(self, domain_name, dns_server):
        print(f"\n[Resolver] Querying {domain_name}...")

        # 1. Check Cache
        records = self.cache.get(domain_name, [])
        valid_records = [rec for rec in records if not rec.is_expired()]

        if valid_records:
            print("   -> Cache hit! Returning from memory.")
            final_records = valid_records

        else:
            if records:
                print("   -> Cache found but expired. Cleaning up...")
                self.cache[domain_name] = []

            # 2. Fetch from Server if cache miss
            print("   -> Cache MISS. Asking Authoritative Server...")
            fetched_records = dns_server.resolve(domain_name)

            if fetched_records:
                self.cache[domain_name] = fetched_records
                print(f"   -> Fetched {len(fetched_records)} record(s) from server.")
                final_records = fetched_records
            else:
                print("   -> Domain not found on server.")
                return []

        # 3. CNAME Handling (The Recursive Logic)
        # If the result is a CNAME, we must automatically look up the target.
        first_record = final_records[0]

        if first_record.record_type == RECORD_CNAME:
            alias_target = first_record.value
            print(f"   [!] Found CNAME (Alias). Automatically following: {alias_target}")

            # RECURSION: We call this same function again!
            return self.query(alias_target, dns_server)

        return self.apply_load_balancing(final_records)

    def reverse_query(self, ip_address, dns_server):
        """
        Performs reverse DNS lookup (IP address -> hostname).
        Similar to query() but uses reverse_lookup() instead of resolve().

        Args:
            ip_address (str): The IP address to look up (e.g., "8.8.8.8")
            dns_server (DNSZone): The authoritative DNS server to query

        Returns:
            list: A list of PTR DNSRecord objects, or empty list if not found.
        """
        print(f"\n[Resolver] Reverse Querying {ip_address}...")

        # 1. Check Cache (use IP as cache key)
        records = self.cache.get(ip_address, [])
        valid_records = [rec for rec in records if not rec.is_expired()]

        if valid_records:
            print("   -> Cache hit! Returning from memory.")
            return valid_records

        else:
            if records:
                print("   -> Cache found but expired. Cleaning up...")
                self.cache[ip_address] = []

            # 2. Fetch from Server if cache miss
            print("   -> Cache MISS. Asking Authoritative Server for reverse lookup...")
            fetched_records = dns_server.reverse_lookup(ip_address)

            if fetched_records:
                self.cache[ip_address] = fetched_records
                print(f"   -> Fetched {len(fetched_records)} PTR record(s) from server.")
                return fetched_records
            else:
                print("   -> IP not found in reverse DNS server.")
                return []

    def apply_load_balancing(self, records):
        """
        Applies load balancing to multiple records.
        For A/AAAA records, returns one using round-robin.
        For other types, returns all records.
        """
        if not records:
            return records

        # Only apply load balancing to A and AAAA records
        if records[0].record_type in [RECORD_A, RECORD_AAAA]:
            # Round-robin: cycle through available records
            domain = records[0].name
            if domain not in self.round_robin_index:
                self.round_robin_index[domain] = 0

            selected_record = records[self.round_robin_index[domain]]
            self.round_robin_index[domain] = (self.round_robin_index[domain] + 1) % len(records)

            print(f"   -> Load Balancing: Selected {selected_record.value} from {len(records)} available IPs")
            return [selected_record]

        # For other record types (MX, CNAME, etc.), return all
        return records

# --- Test Area ---
if __name__ == "__main__":
    root_server = DNSZone()
    print("--- Server Startup ---")

    # 1. Multiple A records for load balancing
    root_server.add_record(DNSRecord("google.com", RECORD_A, "8.8.8.8", 60))
    root_server.add_record(DNSRecord("google.com", RECORD_A, "8.8.4.4", 60))  # Google's secondary DNS
    root_server.add_record(DNSRecord("google.com", RECORD_A, "142.250.190.46", 60))  # Another Google IP

    # 2. The Alias
    root_server.add_record(DNSRecord("www.google.com", RECORD_CNAME, "google.com", 60))

    # 3. PTR records for reverse DNS (IP -> hostname)
    # 8.8.8.8 -> 8.8.8.8.in-addr.arpa -> dns.google
    root_server.add_record(DNSRecord("8.8.8.8.in-addr.arpa", RECORD_PTR, "dns.google", 60))
    # 8.8.4.4 -> 4.4.8.8.in-addr.arpa -> dns.google
    root_server.add_record(DNSRecord("4.4.8.8.in-addr.arpa", RECORD_PTR, "dns.google", 60))
    # 192.168.1.1 -> 1.1.168.192.in-addr.arpa -> router.local
    root_server.add_record(DNSRecord("1.1.168.192.in-addr.arpa", RECORD_PTR, "router.local", 60))

    my_isp = RecursiveResolver()

    # TEST: Multiple queries to demonstrate round-robin load balancing
    print("\n--- Testing Load Balancing with Multiple Queries ---")

    for i in range(5):
        print(f"\n--- Query {i+1} ---")
        final_answer = my_isp.query("www.google.com", root_server)

        print("--- Final Answer for Client ---")
        if final_answer:
            for r in final_answer:
                print(f"  {r}")
        else:
            print("  No records found")

    # TEST: Reverse DNS lookups (IP -> hostname)
    print("\n--- Testing Reverse DNS (IP -> Hostname) ---")

    reverse_tests = ["8.8.8.8", "8.8.4.4", "192.168.1.1", "1.2.3.4"]  # Last one should fail

    for ip in reverse_tests:
        print(f"\n--- Reverse Query for {ip} ---")
        ptr_records = my_isp.reverse_query(ip, root_server)

        print("--- PTR Records Found ---")
        if ptr_records:
            for r in ptr_records:
                print(f"  {r}")
        else:
            print(f"  No PTR record found for {ip}")

    print("\n--- CCNA Reverse DNS Concept Summary ---")
    print("• Forward DNS: hostname -> IP (A records)")
    print("• Reverse DNS: IP -> hostname (PTR records)")
    print("• Format: Reverse IP octets + '.in-addr.arpa'")
    print("• Example: 8.8.8.8 -> 8.8.8.8.in-addr.arpa -> dns.google")