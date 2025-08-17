# Smart boot: auto R/W for persistence, safe R/O for USB & A-button override
import board
import digitalio
import storage
import supervisor

# Read BUTTON A (pull-up; pressed == False)
btn_a = digitalio.DigitalInOut(board.BUTTON_A)
btn_a.switch_to_input(pull=digitalio.Pull.UP)
a_pressed = (btn_a.value is False)

# Detect USB connection (MSC/CDC)
usb_connected = getattr(supervisor.runtime, "usb_connected", False) or \
                getattr(supervisor.runtime, "serial_connected", False)

# Policy:
# - If USB connected -> READ-ONLY (allow host file copy)
# - Else if A held -> READ-ONLY (manual override)
# - Else -> READ-WRITE (enable on-device persistence)
allow_local_write = (not usb_connected) and (not a_pressed)

# Apply mount
# storage.remount(path, readonly)
storage.remount("/", not allow_local_write)

# Helpful breadcrumbs end up in boot_out.txt on CIRCUITPY
if usb_connected:
    print("boot.py: USB detected -> mounting READ-ONLY for safe host file transfer")
elif a_pressed:
    print("boot.py: A-button override -> mounting READ-ONLY")
else:
    print("boot.py: No USB & no override -> mounting READ-WRITE (persistence enabled)")
