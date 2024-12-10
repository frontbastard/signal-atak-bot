import asyncio
import json
import os
import xml.etree.ElementTree as ET
import pytak
from configparser import ConfigParser
import argparse
from decouple import config as pdconfig

UID_COUNTS_FILE = "uid_counts_dict.json"


def load_uid_counts():
    """Load uid counts from a file."""
    if os.path.exists(UID_COUNTS_FILE):
        with open(UID_COUNTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_uid_counts(uid_counts):
    """Save uid counts to a file"""
    with open(UID_COUNTS_FILE, "w") as f:
        json.dump(uid_counts, f)


uid_counts = load_uid_counts()


def generate_unique_uid(base_uid):
    """Generates a unique uid based on the base identifier."""
    if base_uid not in uid_counts:
        uid_counts[base_uid] = 0
    uid_counts[base_uid] += 1
    save_uid_counts(uid_counts)
    return f"{base_uid}-{uid_counts[base_uid]}"


def gen_cot(lat, lon, uid):
    """Generate CoT Event."""
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "a-h-G-U")  # Type of marker
    root.set("uid", uid)  # Unique identifier
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set(
        "stale", pytak.cot_time(300)
    )  # Time difference in seconds from "start" when stale initiates

    pt_attr = {
        "lat": lat,  # Latitude
        "lon": lon,  # Longitude
        "hae": "10.0",
        "ce": "10.0",
        "le": "10.0",
    }

    ET.SubElement(root, "point", attrib=pt_attr)

    detail = ET.SubElement(root, "detail")
    contact = ET.SubElement(detail, "contact")
    contact.set("type", "v")
    contact.set("name", uid)  # Use uid as the name
    contact.set("category", "Enemy")
    contact.set("droid", "ANDROID-1234567890")

    note = ET.SubElement(detail, "note")
    note.text = f"Enemy {uid}"

    return ET.tostring(root, encoding="unicode")


class MySender(pytak.QueueWorker):
    """Defines how you process or generate your Cursor-On-Target Events."""

    def __init__(self, tx_queue, config, lat, lon, uid):
        super().__init__(tx_queue, config)
        self.lat = lat
        self.lon = lon
        self.uid = uid

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, then puts on queue."""
        event = data.encode("utf-8")  # Convert to bytes
        await self.put_queue(event)

    async def run(self, number_of_iterations=-1):
        """Run the loop for processing or generating pre-CoT data."""
        while 1:
            data = gen_cot(self.lat, self.lon, self.uid)
            self._logger.info("Sending:\n%s\n", data)
            await self.handle_data(data)
            await asyncio.sleep(5)


class MyReceiver(pytak.QueueWorker):
    """Defines how you will handle events from RX Queue."""

    async def handle_data(self, data):
        """Handle data from the receive queue."""
        self._logger.info("Received:\n%s\n", data.decode())

    async def run(self):  # pylint: disable=arguments-differ
        """Read from the receive queue, put data onto handler."""
        while 1:
            data = (
                await self.queue.get()
            )  # this is how we get the received CoT from rx_queue
            await self.handle_data(data)


async def main(lat, lon, base_uid):
    """Main definition of your program, sets config params and
    adds your serializer to the asyncio task list.
    """
    config = ConfigParser()
    config["botsignal"] = {
        "COT_URL": f"tcp://"
                   f"{pdconfig("ATAK_HOST", default="137.184.101.250")}:"
                   f"{pdconfig("ATAK_PORT", default="8087")}"
    }
    config = config["botsignal"]

    unique_uid = generate_unique_uid(base_uid)

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add a serializer to the asyncio task list.
    clitool.add_tasks(
        {
            MySender(clitool.tx_queue, config, lat, lon, unique_uid),
            MyReceiver(clitool.rx_queue, config)
        }
    )

    # Start all tasks.
    await clitool.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send CoT event to ATAK.")
    parser.add_argument(
        "latitude", type=str, help="Latitude of the event location."
    )
    parser.add_argument(
        "longitude", type=str, help="Longitude of the event location."
    )
    parser.add_argument(
        "base_uid", type=str, help="Base identifier for the event."
    )

    args = parser.parse_args()

    asyncio.run(main(args.latitude, args.longitude, args.base_uid))
