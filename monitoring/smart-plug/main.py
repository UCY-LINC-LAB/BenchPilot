import asyncio
import os
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from prometheus_client import Gauge, start_http_server

smart_plug_num = str(os.getenv("SMART_PLUG_NUM"))
# Prometheus Gauge for power consumption
power_gauge = Gauge('smart_plug_power_W', 'Power consumption of the smart plug')

async def fetch_power_metrics(plug):
    while True:
        try:
            # Fetch the latest consumption data
            power = await plug.async_get_instant_metrics()
            power_gauge.set(power.power)
        except Exception as e:
            print(f"Error fetching power metrics: {e}")
        # Wait before fetching the next set of metrics
        await asyncio.sleep(10)  # TODO: Adjust the sleep time as needed

async def main():
    # TODO: don't forget to set your meross email and password
    email = os.getenv("MEROSS_EMAIL")
    password = os.getenv("MEROSS_PASSWORD")

    if not email or not password:
        print("Email or password environment variables are missing.")
        return

    # Initialize the Meross Manager
    # TODO: you can change the api_base_url depending on your account
    client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-us.meross.com', email=email, password=password)
    manager = MerossManager(http_client=client)
    
    # Login to the Meross Cloud
    await manager.async_init() 
    
    # Load known devices
    await manager.async_device_discovery()
    
    # Retrieve the device
    plugs = manager.find_devices(device_type="mss310") # TODO: update the device_type based on your device
    if len(plugs) < 1:
        print("No MSS310 plugs found...")
        return

    myplug = plugs[0]
    for plug in plugs:
        if str(plug).split(" (")[0] == f"smart-plug-{smart_plug_num}":
            myplug = plug

    # Start fetching power metrics
    await fetch_power_metrics(myplug)

    # Close the manager properly when done (this will actually never be called in this loop)
    await manager.async_close()

if __name__ == "__main__":
    # Start Prometheus server on port 19998, which Netdata can scrape
    start_http_server(19998)

    # Run the asyncio loop to fetch metrics continuously
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
