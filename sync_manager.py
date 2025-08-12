# Charles Doebler at Feral Cat AI
# Bluetooth sync manager for synchronized UFO dance parties

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import json
import time

class SyncManager:
    def __init__(self, device_name, is_leader=False, debug_bluetooth=False):
        self.debug_bluetooth = debug_bluetooth
        
        if self.debug_bluetooth:
            print("[BLE] === SYNC MANAGER INIT ===")
            print("[BLE] Device: %s, Leader: %s" % (device_name, is_leader))
        
        self.device_name = device_name
        self.is_leader = is_leader
        self.connection = None
        self.uart_service = None  # Initialize as None
        
        # Initialize BLE
        try:
            self.ble = BLERadio()
            
            # Stop any existing advertising or connections
            if self.ble.advertising:
                if self.debug_bluetooth:
                    print("[BLE] Stopping existing advertising...")
                self.ble.stop_advertising()
            
            if self.ble.connected:
                if self.debug_bluetooth:
                    print("[BLE] Disconnecting existing connections...")
                for connection in self.ble.connections:
                    connection.disconnect()
            
            if self.debug_bluetooth:
                print("[BLE] Radio initialized and cleaned")
            
            # Only create UART service for leader
            if is_leader:
                self.uart_service = UARTService()
                if self.debug_bluetooth:
                    print("[BLE] UART Service created for leader")
                self.advertisement = ProvideServicesAdvertisement(self.uart_service)
                if self.debug_bluetooth:
                    print("[BLE] Advertisement created")
            
        except (OSError, RuntimeError, MemoryError) as init_error:
            print("[BLE] Init Error: %s" % str(init_error))
            return
        
        # Setup BLE based on role
        if is_leader:
            self._setup_as_leader()
        else:
            self._setup_as_follower()

    def _setup_as_leader(self):
        """Setup as leader - advertises and accepts connections."""
        try:
            leader_name = "%s_LEADER" % self.device_name
            self.ble.name = leader_name
            if self.debug_bluetooth:
                print("[BLE] Set leader name: %s" % leader_name)
        
            if self.debug_bluetooth:
                print("[BLE] Starting advertising...")
            self.ble.start_advertising(self.advertisement)
            print("[BLE] ✅ LEADER: Advertising started")
            if self.debug_bluetooth:
                print("[BLE] Leader will continue advertising for multiple followers...")
        
        except Exception as e:
            print("[BLE] ❌ Leader setup error: %s" % str(e))

    def _setup_as_follower(self):
        """Setup as follower - scans for leader."""
        try:
            follower_name = "%s_FOLLOWER" % self.device_name
            self.ble.name = follower_name
            if self.debug_bluetooth:
                print("[BLE] Set follower name: %s" % follower_name)
                print("[BLE] ✅ FOLLOWER: Ready to scan for leader")
        
        except Exception as e:
            print("[BLE] ❌ Follower setup error: %s" % str(e))

    def broadcast_pattern(self, pattern_data):
        """Leader broadcasts a light pattern to all followers."""
        if not self.is_leader:
            return
            
        try:
            # Keep advertising active for new followers to join
            if not self.ble.advertising:
                if self.debug_bluetooth:
                    print("[BLE] Restarting advertising for new followers...")
                self.ble.start_advertising(self.advertisement)
        
            # Check if anyone is connected
            connected_count = len(self.ble.connections)
            if connected_count == 0:
                if self.debug_bluetooth:
                    print("[BLE] No followers connected to leader")
                return
        
            # Send pattern data
            packet = {
                'type': 'dance_pattern',
                'pixels': pattern_data.get('pixels', []),
                'beat': pattern_data.get('beat', False)
            }
            data = json.dumps(packet).encode('utf-8')
            packet_size = len(data)
        
            if packet_size < 200:
                # Send data to each connected follower
                for connection in self.ble.connections:
                    if connection.connected and UARTService in connection:
                        try:
                            uart = connection[UARTService]
                            uart.write(data + b'\n')
                            if self.debug_bluetooth:
                                print("[BLE] Sent to connection: %s" % str(connection))
                        except (OSError, RuntimeError) as write_error:
                            print("[BLE] ❌ Write error to connection: %s" % str(write_error))
                
                print("[BLE] Sent pattern to %d followers: Beat=%s, Pixels=%d" % 
                      (connected_count, packet.get('beat'), len(packet.get('pixels', []))))
            else:
                print("[BLE] ⚠️ Data packet is too large: %d bytes" % packet_size)
            
        except (OSError, RuntimeError, MemoryError) as broadcast_error:
            print("[BLE] ❌ Broadcast error: %s" % str(broadcast_error))


    def receive_pattern(self):
        """Follower receives a pattern from the leader."""
        if self.is_leader:
            if self.debug_bluetooth:
                print("[BLE] Cannot receive - this device is a leader")
            return None
            
        if not self.connection or not self.connection.connected:
            if self.debug_bluetooth:
                print("[BLE] Cannot receive - no active connection")
            return None
            
        if not self.uart_service:
            if self.debug_bluetooth:
                print("[BLE] Cannot receive - no UART service")
            return None
    
        data = None  # Initialize data variable
        
        try:
            if self.debug_bluetooth:
                print("[BLE] Checking for data, in_waiting: %d" % self.uart_service.in_waiting)
            
            if self.uart_service.in_waiting > 0:
                data_waiting = self.uart_service.in_waiting
                print("[BLE] Receiving pattern data, bytes: %d" % data_waiting)
            
                data = self.uart_service.read(data_waiting)
                if data:
                    if self.debug_bluetooth:
                        print("[BLE] Raw data received: %s" % data[:50])
                    
                    # Handle multiple packets or incomplete data
                    packet_str = data.decode('utf-8').strip()
                    
                    # Remove newline characters that might split packets
                    packet_str = packet_str.replace('\n', '')
                    
                    if packet_str:
                        packet = json.loads(packet_str)
                    
                        if packet.get('type') == 'dance_pattern':
                            print("[BLE] ✅ Received valid pattern: Beat=%s, Pixels=%d" % 
                                  (packet.get('beat'), len(packet.get('pixels', []))))
                            return packet
                        else:
                            print("[BLE] ⚠️ Invalid packet type: %s" % packet.get('type'))
                    else:
                        if self.debug_bluetooth:
                            print("[BLE] Empty packet string after decoding")
        
            if self.debug_bluetooth:
                print("[BLE] No data available to receive")
                
        except (OSError, RuntimeError, AttributeError) as uart_error:
            print("[BLE] ❌ UART error: %s" % str(uart_error))
        except (UnicodeDecodeError, ValueError) as decode_error:
            print("[BLE] ❌ Data decode error: %s, raw data: %s" % 
                  (str(decode_error), data[:50] if data else 'None'))
        
        return None

    def try_connect_to_leader(self):
        """Follower attempts to connect to a leader."""
        if self.is_leader:
            return False
            
        if self.debug_bluetooth:
            print("[BLE] 🔍 Scanning for dance leader...")
        
        try:
            scan_results = 0
            found_leader = False
            
            for advertisement in self.ble.start_scan(timeout=10):
                scan_results += 1
                adv_name = advertisement.complete_name
                
                if adv_name and self.debug_bluetooth:
                    print("[BLE] Found: %s" % adv_name)
                    
                if adv_name and "_LEADER" in adv_name:
                    print("[BLE] 🎯 Found leader: %s" % adv_name)
                    found_leader = True
                    
                    try:
                        if self.debug_bluetooth:
                            print("[BLE] Connecting...")
                        
                        self.connection = self.ble.connect(advertisement)
                        
                        if self.debug_bluetooth:
                            print("[BLE] Connection object created, waiting for services...")
                        
                        # Wait for a connection to establish and discover services
                        connection_timeout = 0
                        max_connection_wait = 10
                        
                        while connection_timeout < max_connection_wait:
                            if self.connection and self.connection.connected:
                                if self.debug_bluetooth:
                                    print("[BLE] Connection established, discovering services...")
                                
                                try:
                                    # Get the UART service from the connection
                                    if UARTService in self.connection:
                                        self.uart_service = self.connection[UARTService]
                                        if self.debug_bluetooth:
                                            print("[BLE] UART service acquired from connection")
                                            print("[BLE] Service: %s" % str(self.uart_service))
                                        
                                        # Test the service by checking if it has the expected attributes
                                        if hasattr(self.uart_service, 'in_waiting'):
                                            print("[BLE] ✅ Connected successfully with working UART service!")
                                            self.ble.stop_scan()
                                            return True
                                        else:
                                            if self.debug_bluetooth:
                                                print("[BLE] UART service missing in_waiting attribute")
                                    else:
                                        if self.debug_bluetooth:
                                            print("[BLE] UART service not found in connection")
                                        time.sleep(0.5)
                                        connection_timeout += 0.5
                                except (OSError, RuntimeError, AttributeError) as service_error:
                                    if self.debug_bluetooth:
                                        print("[BLE] Service discovery error: %s" % str(service_error))
                                    time.sleep(0.5)
                                    connection_timeout += 0.5
                            else:
                                if self.debug_bluetooth:
                                    print("[BLE] Waiting for connection... (%ds)" % connection_timeout)
                                time.sleep(1)
                                connection_timeout += 1
                        
                        print("[BLE] ❌ Connection timeout after %d seconds" % max_connection_wait)
                        
                        # Clean up failed connection
                        if self.connection:
                            try:
                                self.connection.disconnect()
                            except (OSError, RuntimeError):
                                pass
                            self.connection = None
                            
                    except (OSError, RuntimeError, ConnectionError) as connect_error:
                        print("[BLE] ❌ Connect failed: %s" % str(connect_error))
                        if self.connection:
                            try:
                                self.connection.disconnect()
                            except (OSError, RuntimeError):
                                pass
                            self.connection = None
                        
            self.ble.stop_scan()
            
            if not found_leader:
                print("[BLE] ❌ No leader found")
            if self.debug_bluetooth:
                print("[BLE] Total devices found: %d" % scan_results)
            
        except (OSError, RuntimeError, MemoryError) as scan_error:
            print("[BLE] ❌ Scan error: %s" % str(scan_error))
        
        return False

    def get_connection_status(self):
        """Get a detailed connection status for debugging."""
        try:
            if self.is_leader:
                connection_count = len(self.ble.connections)
                print("[BLE] Leader connection status: %d followers connected" % connection_count)
                return connection_count > 0
            else:
                if self.connection and self.connection.connected:
                    print("[BLE] Follower connection active")
                    return True
                else:
                    print("[BLE] Follower not connected")
                    return False
        except Exception as e:
            print("[BLE] ❌ Error checking connection status: %s" % str(e))
            return False
