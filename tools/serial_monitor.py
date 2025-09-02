import serial
import serial.tools.list_ports
import time
import threading
import sys

class CircuitPlaygroundSerial:
    def __init__(self, port='COM7', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.running = False
        
    def find_circuitpython_port(self):
        """Automatically find CircuitPython device port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # CircuitPython devices typically show up with these identifiers
            if any(identifier in port.description.lower() for identifier in 
                   ['circuitpython', 'circuit playground', 'adafruit']):
                print(f"Found CircuitPython device on {port.device}")
                return port.device
        return None
    
    def connect(self):
        """Connect to the Circuit Playground"""
        try:
            # Auto-detect port if not specified
            if not self.port or self.port == 'AUTO':
                detected_port = self.find_circuitpython_port()
                if detected_port:
                    self.port = detected_port
                else:
                    print("No CircuitPython device found")
                    return False
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,
                write_timeout=1
            )
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring serial output"""
        if not self.connect():
            return
            
        self.running = True
        
        def read_serial():
            while self.running:
                try:
                    if self.serial_connection and self.serial_connection.in_waiting > 0:
                        line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(f"[{time.strftime('%H:%M:%S')}] {line}")
                except serial.SerialException as e:
                    print(f"Serial read error: {e}")
                    break
                except UnicodeDecodeError:
                    # Skip lines that can't be decoded
                    pass
                time.sleep(0.01)
        
        # Start reading in a separate thread
        read_thread = threading.Thread(target=read_serial, daemon=True)
        read_thread.start()
        
        print("Serial monitor started. Press Ctrl+C to stop, or type commands:")
        
        try:
            while self.running:
                # Allow sending commands to the device
                user_input = input()
                if user_input.lower() in ['exit', 'quit', 'stop']:
                    break
                elif user_input and self.serial_connection:
                    # Send command to Circuit Playground (triggers REPL if needed)
                    self.serial_connection.write((user_input + '\r\n').encode())
                    
        except KeyboardInterrupt:
            print("\nStopping serial monitor...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the serial connection"""
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed")

def main():
    # You can specify the port or use 'AUTO' for auto-detection
    monitor = CircuitPlaygroundSerial(port='COM7', baudrate=115200)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
