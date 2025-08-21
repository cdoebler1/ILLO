import board
import digitalio
import storage
import supervisor
import time

time.sleep(0.2)

# Use the slide switch instead of buttons (more reliable)
switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.switch_to_input(pull=digitalio.Pull.UP)

switch_readings = []
for i in range(5):
    switch_readings.append(switch.value)
    time.sleep(0.05)

# Switch in "ON" position (True) = enable write mode
switch_on = sum(switch_readings) >= 3

# USB detection
try:
    usb_connected = supervisor.runtime.usb_connected or supervisor.runtime.serial_connected
except:
    usb_connected = False

if not usb_connected:
    storage.remount("/", readonly=False)
    print("boot.py: Standalone - READ-WRITE")
elif usb_connected and switch_on:
    storage.remount("/", readonly=False)
    print("boot.py: USB + Switch ON - READ-WRITE (testing mode)")
else:
    storage.remount("/", readonly=True)
    print("boot.py: USB + Switch OFF - READ-ONLY")

print("boot.py: USB:", usb_connected, "Switch readings:", switch_readings, "Final:", switch_on)
