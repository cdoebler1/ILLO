# Charles Doebler at Feral Cat AI
# Bluetooth Controller for Intergalactic Cruising - Bluefruit Connect App Interface

import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService


class BluefruitController:
    def __init__(self, debug=False):
        self.debug = debug
        self.ble = None
        self.uart_service = None
        self.connection = None
        self.last_command_time = 0

        # NEW: Advertising management
        self.advertising_start_time = 0
        self.advertising_timeout = 120  # 2 minutes default
        self.auto_readvertise = True  # Re-advertise periodically
        self.last_readvertise = 0
        self.readvertise_interval = 300  # 5 minutes between re-advertising

        # Connection history for reconnection
        self.known_devices = []  # Could store bonded device info
        self.connection_attempts = 0

        # Intergalactic Cruising specific controls
        self.bluetooth_mode_override = None  # Override color mode via Bluetooth
        self.bluetooth_brightness = None  # Override brightness
        self.manual_beat_trigger = False  # Manual beat sync
        self.rotation_speed_modifier = 1.0  # Speed up/slow down rotation
        self.color_override = None  # Direct color control
        self.effect_modifier = "normal"  # Effect intensity modifier

        # Initialize BLE - SIMPLIFIED VERSION LIKE THE WORKING SAMPLE
        try:
            self.ble = BLERadio()
            
            # Clean slate - disconnect any existing connections
            if self.ble.connected:
                for connection in self.ble.connections:
                    connection.disconnect()
            
            if self.ble.advertising:
                self.ble.stop_advertising()

            # Create UART service - this is the key fix
            self.uart_service = UARTService()
            
            # Create advertisement with UART service
            self.advertisement = ProvideServicesAdvertisement(self.uart_service)
            self.advertisement.complete_name = "ILLO_CRUISER"
            
            # Set radio name
            self.ble.name = "ILLO_CRUISER"

            if self.debug:
                print("[BT] Bluefruit Controller initialized")
                print("[BT] UART Service created: %s" % str(self.uart_service))

        except Exception as e:
            print("[BT] Bluetooth initialization failed: %s" % str(e))
            self.ble = None

    def enable_debug(self):
        """Enable debug output."""
        self.debug = True
        print("[BT] Debug output enabled")

    def disable_debug(self):
        """Disable debug output."""
        self.debug = False
        print("[BT] Debug output disabled")

    def start_advertising(self, timeout_seconds=120):
        """Start advertising with configurable timeout."""
        if not self.ble:
            return False

        try:
            if self.ble.advertising:
                self.ble.stop_advertising()

            self.ble.start_advertising(self.advertisement)
            self.advertising_start_time = time.monotonic()
            self.advertising_timeout = timeout_seconds

            print("[BT] 📱 Advertising for %d seconds..." % timeout_seconds)
            if self.debug:
                print(
                    "[BT] Users have %d seconds to connect via Bluefruit Connect app" % timeout_seconds)
            return True

        except Exception as e:
            print("[BT] Failed to start advertising: %s" % str(e))
            return False

    def manage_advertising(self):
        """Manage advertising lifecycle - call this regularly in main loop."""
        if not self.ble:
            return

        current_time = time.monotonic()

        try:
            # If we're advertising, check if we should stop
            if self.ble.advertising:
                advertising_duration = current_time - self.advertising_start_time

                if advertising_duration > self.advertising_timeout:
                    self.ble.stop_advertising()
                    print(
                        "[BT] ⏰ Advertising timeout after %d seconds" % self.advertising_timeout)
                    if self.debug:
                        print(
                            "[BT] To reconnect: Use Bluefruit Connect app's 'Connect' history")

            # Auto re-advertise periodically if enabled and no connection
            elif self.auto_readvertise and not self.is_connected():
                time_since_last = current_time - self.last_readvertise

                if time_since_last > self.readvertise_interval:
                    print("[BT] 🔄 Auto re-advertising for new connections...")
                    self.start_advertising(self.advertising_timeout)
                    self.last_readvertise = current_time

        except Exception as e:
            if self.debug:
                print("[BT] Advertising management error: %s" % str(e))

    def is_connected(self):
        """Check if we have an active connection - simplified version."""
        try:
            return (self.connection and 
                    self.connection.connected and 
                    self.uart_service is not None)
        except:
            return False

    def check_connection(self):
        """Simplified connection checking based on working sample pattern."""
        if not self.ble:
            if self.debug:
                print("[BT] No BLE radio available")
            return False

        try:
            # Simple connection check - we ARE the peripheral, not looking for services
            if self.ble.connected:
                if self.debug:
                    print("[BT] BLE connected: %s, connections: %d" % 
                          (self.ble.connected, len(self.ble.connections)))
                
                # Get the first connection
                if len(self.ble.connections) > 0:
                    current_connection = self.ble.connections[0]
                    
                    if current_connection.connected:
                        # We don't need to find UART in the connection - WE provide it
                        if not self.connection:
                            print("[BT] ✅ New device connected!")
                            self.connection = current_connection
                            # We already have uart_service from init - just use it
                            
                            # Stop advertising when connected
                            if self.ble.advertising:
                                self.ble.stop_advertising()
                                if self.debug:
                                    print("[BT] Stopped advertising - device connected")

                            # Send welcome message
                            self.send_response("ILLO Intergalactic Cruising ready!\nType /help for commands")
                            
                        return True
                    else:
                        # Connection was lost
                        if self.connection:
                            self.handle_disconnection()
                        return False
                        
            else:
                # No connections
                if self.connection:
                    self.handle_disconnection()
                return False

        except Exception as e:
            if self.debug:
                print("[BT] Connection check error: %s" % str(e))
            return False

    def handle_disconnection(self):
        """Handle when a device disconnects."""
        if self.connection:
            print("[BT] 📱 Device disconnected")
            self.connection = None
            self.uart_service = None

            # Optionally restart advertising for new connections
            if self.auto_readvertise:
                print("[BT] 🔄 Restarting advertising for reconnection...")
                self.start_advertising(60)  # Shorter timeout for reconnection

    def set_advertising_config(self, timeout_seconds=120, auto_readvertise=True,
                               readvertise_interval=300):
        """Configure advertising behavior."""
        self.advertising_timeout = timeout_seconds
        self.auto_readvertise = auto_readvertise
        self.readvertise_interval = readvertise_interval

        print("[BT] Advertising config: %ds timeout, auto-readvertise: %s" %
              (timeout_seconds, auto_readvertise))

    def process_commands(self):
        """Process incoming commands from Bluefruit Connect app."""
        if not self.connection or not self.uart_service:
            return

        try:
            if self.uart_service.in_waiting > 0:
                data = self.uart_service.read(self.uart_service.in_waiting)
                if data:
                    command_str = data.decode('utf-8').strip()
                    if self.debug:
                        print("[BT] Received: %s" % command_str)

                    self._parse_command(command_str)

        except Exception as e:
            if self.debug:
                print("[BT] Command processing error: %s" % str(e))

    def _parse_command(self, command_str):
        """Parse commands from Bluefruit Connect app."""

        try:
            # Handle Control Pad commands (button presses)
            if command_str.startswith('!B'):
                self._handle_control_pad(command_str)

            # Handle Color Picker commands
            elif command_str.startswith('!C'):
                self._handle_color_picker(command_str)

            # Handle UART text commands
            elif command_str.startswith('/'):
                self._handle_text_commands(command_str[1:])  # Remove leading '/'

            # Handle sensor data (for beat detection)
            elif command_str.startswith('!A') or command_str.startswith('!G'):
                self._handle_sensor_data(command_str)

        except Exception as e:
            if self.debug:
                print("[BT] Command parse error: %s" % str(e))

    def _handle_control_pad(self, command):
        """Handle Control Pad button presses."""
        # Control Pad format: !B<button><state> (e.g., !B11 = button 1 pressed, !B10 = button 1 released)
        try:
            if self.debug:
                print("[BT] Processing control pad command: %s" % command)
                
            button_num = int(command[2])
            button_state = int(command[3])
            
            if self.debug:
                print("[BT] Button %d, State %d" % (button_num, button_state))

            if button_state == 1:  # Button pressed
                if button_num == 1:  # Up button
                    print("[BT] 🎨 Mode: Rainbow Wheel")
                    self._simulate_button_b_press(1)

                elif button_num == 2:  # Down button  
                    print("[BT] 🎨 Mode: Pink Nebula")
                    self._simulate_button_b_press(2)

                elif button_num == 3:  # Left button
                    print("[BT] 🎨 Mode: Deep Space Blue")
                    self._simulate_button_b_press(3)

                elif button_num == 4:  # Right button
                    print("[BT] 🎨 Mode: Forest Canopy")
                    self._simulate_button_b_press(4)

                elif button_num == 5:  # Button 1 (center/select)
                    print("[BT] 🥁 Manual Beat Trigger!")
                    self.manual_beat_trigger = True

                elif button_num == 6:  # Button 2
                    print("[BT] ⚡ Effect: Enhanced")
                    self.effect_modifier = "enhanced"

                elif button_num == 7:  # Button 3
                    print("[BT] 💫 Effect: Gentle")
                    self.effect_modifier = "gentle"

                elif button_num == 8:  # Button 4
                    print("[BT] 🔄 Reset to Audio Mode")
                    self.bluetooth_mode_override = None
                    self.color_override = None
                    self.effect_modifier = "normal"

        except (ValueError, IndexError) as e:
            print("[BT] Control pad parse error: %s" % str(e))

    def _simulate_button_b_press(self, target_mode):
        """Simulate a Button B press to change mode and persist to config."""
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.load_config()
            
            # Change the mode in config
            config['mode'] = target_mode
            save_success = config_mgr.save_config(config)
            
            if save_success:
                print("[BT] Mode changed to %d and saved to config" % target_mode)
            else:
                print("[BT] Mode changed to %d but save failed (read-only filesystem?)" % target_mode)
            
            # Always set the bluetooth override for immediate effect (even if save fails)
            self.bluetooth_mode_override = target_mode
            
        except Exception as e:
            print("[BT] Failed to simulate button press: %s" % str(e))
            # Fallback to just setting the override
            self.bluetooth_mode_override = target_mode
            print("[BT] Using fallback: Mode override set to %d" % target_mode)

    def _handle_color_picker(self, command):
        """Handle Color Picker input."""
        # Color format: !C<R><G><B> where RGB are hex values
        try:
            if len(command) == 8:  # !C + 6 hex chars
                hex_color = command[2:]
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)

                self.color_override = (r, g, b)
                print("[BT] 🎨 Custom Color: (%d,%d,%d)" % (r, g, b))

        except (ValueError, IndexError) as e:
            if self.debug:
                print("[BT] Color picker parse error: %s" % str(e))

    def _handle_text_commands(self, command):
        """Handle text-based commands via UART terminal."""
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return

        cmd = cmd_parts[0]

        if cmd == 'help':
            self.send_response("ILLO Intergalactic Cruising Commands:\n" +
                               "/speed <0.1-3.0> - Rotation speed\n" +
                               "/brightness <0-100> - Brightness level\n" +
                               "/mode <1-4> - Color mode\n" +
                               "/beat - Manual beat trigger\n" +
                               "/status - Show current settings")

        elif cmd == 'speed' and len(cmd_parts) > 1:
            try:
                speed = float(cmd_parts[1])
                if 0.1 <= speed <= 3.0:
                    self.rotation_speed_modifier = speed
                    self.send_response("Rotation speed: %.1fx" % speed)
                else:
                    self.send_response("Speed must be 0.1-3.0")
            except ValueError:
                self.send_response("Invalid speed value")

        elif cmd == 'brightness' and len(cmd_parts) > 1:
            try:
                brightness = int(cmd_parts[1])
                if 0 <= brightness <= 100:
                    self.bluetooth_brightness = brightness / 100.0
                    self.send_response("Brightness: %d%%" % brightness)
                else:
                    self.send_response("Brightness must be 0-100")
            except ValueError:
                self.send_response("Invalid brightness value")

        elif cmd == 'mode' and len(cmd_parts) > 1:
            try:
                mode = int(cmd_parts[1])
                if 1 <= mode <= 4:
                    self.bluetooth_mode_override = mode
                    mode_names = {1: "Rainbow Wheel", 2: "Pink Nebula", 3: "Deep Space Blue", 4: "Forest Canopy"}
                    self.send_response("Mode: %s" % mode_names[mode])
                else:
                    self.send_response("Mode must be 1-4")
            except ValueError:
                self.send_response("Invalid mode value")

        elif cmd == 'beat':
            self.manual_beat_trigger = True
            self.send_response("Manual beat triggered!")

        elif cmd == 'status':
            status = "Current Settings:\n"
            status += "Mode Override: %s\n" % (self.bluetooth_mode_override or "Audio")
            status += "Speed: %.1fx\n" % self.rotation_speed_modifier
            status += "Brightness: %s\n" % ("%.0f%%" % (
                    self.bluetooth_brightness * 100) if self.bluetooth_brightness else "Auto")
            status += "Effect: %s" % self.effect_modifier
            self.send_response(status)

    def _handle_sensor_data(self, command):
        """Handle accelerometer/gyro data for beat detection."""
        try:
            # Accelerometer: !A<x><y><z> or Gyro: !G<x><y><z>
            # Simple threshold-based beat detection from phone movement
            if command.startswith('!A'):
                # Parse accelerometer data (simplified)
                # In a real implementation, you'd analyze the motion patterns
                # For now, just trigger on significant movement
                self.manual_beat_trigger = True
                if self.debug:
                    print("[BT] Motion-based beat trigger")

        except Exception as e:
            if self.debug:
                print("[BT] Sensor data error: %s" % str(e))

    def send_response(self, message):
        """Send response back to Bluefruit Connect app."""
        try:
            if self.uart_service and self.connection and self.connection.connected:
                self.uart_service.write((message + '\n').encode('utf-8'))
                if self.debug:
                    print("[BT] Sent: %s" % message)
        except Exception as e:
            if self.debug:
                print("[BT] Send error: %s" % str(e))

    def get_mode_override(self):
        """Get current mode override from Bluetooth."""
        return self.bluetooth_mode_override

    def get_brightness_override(self):
        """Get current brightness override from Bluetooth."""
        return self.bluetooth_brightness

    def check_manual_beat(self):
        """Check and consume manual beat trigger."""
        if self.manual_beat_trigger:
            self.manual_beat_trigger = False
            return True
        return False

    def get_rotation_speed_modifier(self):
        """Get current rotation speed modifier."""
        return self.rotation_speed_modifier

    def get_color_override(self):
        """Get direct color override from Color Picker."""
        return self.color_override

    def get_effect_modifier(self):
        """Get current effect modifier."""
        return self.effect_modifier

    def cleanup(self):
        """Clean up Bluetooth resources."""
        try:
            if self.ble and self.ble.advertising:
                self.ble.stop_advertising()
            if self.connection:
                self.connection.disconnect()
        except Exception as e:
            if self.debug:
                print("[BT] Cleanup error: %s" % str(e))

    def get_connection_info(self):
        """Get detailed connection status for debugging."""
        try:
            info = {
                'connected': self.is_connected(),
                'advertising': self.ble.advertising if self.ble else False,
                'connection_count': len(self.ble.connections) if self.ble else 0
            }

            if self.ble and self.ble.advertising:
                advertising_time = time.monotonic() - self.advertising_start_time
                info['advertising_remaining'] = max(0,
                                                    int(self.advertising_timeout - advertising_time))

            return info
        except:
            return {'error': 'Unable to get connection info'}
