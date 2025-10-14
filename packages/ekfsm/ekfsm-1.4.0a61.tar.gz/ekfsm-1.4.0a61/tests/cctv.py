import pprint
import logging
from pathlib import Path
import threading
from time import sleep

from ekfsm.system import System

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

config = Path(__file__).parent / "cctv.yaml"
system = System(config, abort=True)

pprint.pprint(f"System slots {system.slots}")

system.print()

print(system.smc.i4e.leds.client._fb_client.connected)

cpu = system["CPU"]
cpuB = system.cpu
cpuC = system[0]

assert cpu == cpuB == cpuC

# To check why below is failing
# cpu_slot = system.slots["SYSTEM_SLOT"]
# cpu_slotB = system.slots.SYSTEM_SLOT
# cpu_slotC = system.slots[0]

# assert cpu_slot == cpu_slotB == cpu_slotC

cpu.print()
print(f"probing CPU: {cpu.probe()}")
print(
    f"inventory: {cpu.inventory.vendor()} {cpu.inventory.model()} {cpu.inventory.serial()}"
)

smc = system.smc

smc.print()

i4e = smc.i4e
i4e.watchdog.kick()
print(i4e.watchdog.client._fb_client.connected)
i4e.leds.led2.set(0, True)
print(system.smc.i4e.leds.client._fb_client.connected)
i4e.leds.led5.set(3, True)
print(system.smc.i4e.leds.client._fb_client.connected)
i4e.leds.led3.set(5, False)
print(system.smc.i4e.leds.client._fb_client.connected)

button_array = i4e.buttons
# print(button_array._client._fb_client.connected)

eject = button_array.eject

eject.handler = lambda: print("Eject pressed")

stop_event = threading.Event()
button_thread = threading.Thread(target=button_array.read, args=(stop_event,))
button_thread.start()

for i in range(30):
    print("Main thread running...")
    # i4e.watchdog.kick()
    # print(i4e.watchdog.client._fb_client.connected)
    # i4e.leds.led2.set(0, True)
    # print(system.smc.i4e.leds.client._fb_client.connected)
    # i4e.leds.led5.set(3, True)
    # print(system.smc.i4e.leds.client._fb_client.connected)
    # i4e.leds.led3.set(5, False)
    # print(system.smc.i4e.leds.client._fb_client.connected)
    sleep(1)

# To stop the thread:
stop_event.set()
button_thread.join()
