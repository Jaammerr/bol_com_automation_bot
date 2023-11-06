import asyncio
import os
import random
import yaml

from loguru import logger
from src.get_excel_data import get_excel_data
from src.main import Automation

try:
    with open("settings.yaml", "r") as f:
        config = yaml.safe_load(f)

except FileNotFoundError:
    logger.error("settings.yaml not found. Please create a settings.yaml file and add the required settings.")
    exit(1)


def initialize_settings() -> None:
    """
    Initializes the config from settings.yaml file
    """

    if config["use_proxy"] is None or config["launch_per_24h"] is None:
        logger.error("Please add the required settings in settings.yaml file.")
        exit(1)

    proxy_path = os.path.join(os.getcwd(), "proxies.txt")
    if config["use_proxy"] and not os.path.exists(proxy_path):
        logger.error("proxies.txt file not found. Please create a proxies.txt file and add the proxies in it.")
        exit(1)

    if not isinstance(config["launch_per_24h"], int) or config["launch_per_24h"] < 1:
        logger.error("launch_per_24h should be an integer and greater than 0.")
        exit(1)


    if config["use_proxy"]:
        with open(proxy_path, "r") as fp:
            config["proxies"] = [proxy.strip() for proxy in fp.readlines()]
            if len(config["proxies"]) == 0:
                logger.error("No proxies found in proxies.txt file.")
                exit(1)

            config["proxies"] = list(set(config["proxies"]))
            for proxy in config["proxies"]:
                if str(proxy).count(":") != 3:
                    logger.error(f"Invalid proxy found: {proxy}")
                    exit(1)



async def run_task(value: tuple[str, str], interval: int, queue: asyncio.Queue = None):
    while True:
        for i in range(config["launch_per_24h"]):
            # Delay between each launch
            delay = random.uniform(interval * i, interval * (i + 1))

            # Get proxy from queue if use_proxy is True
            logger.info(f"Waiting for {delay * 3600} seconds to run task with url {value[1]}")

            await asyncio.sleep(delay * 3600)
            logger.info(f"Running task with url {value[1]}")
            proxy = await queue.get() if queue else None
            await Automation(
                title=value[0],
                url=value[1],
                proxy=proxy,
            ).start()
            await queue.put(proxy) if queue else None


sem = asyncio.Semaphore(config["concurrency_limit"])


async def run_safe_task(value: tuple[str, str], interval: int, queue: asyncio.Queue = None):
    async with sem:
        try:
            return await run_task(value, interval, queue)
        except Exception as e:
            logger.error(f"Error occurred while running task with value {value}: {e}")


async def main() -> None:
    interval = 24 / config["launch_per_24h"]
    values = get_excel_data()

    if config["use_proxy"]:
        queue = asyncio.Queue()
        for proxy in config["proxies"]:
            queue.put_nowait(proxy)

    else:
        queue = None

    logger.info(f"Found {len(values)} tasks to run | Launching {config['launch_per_24h']} times per 24 hours")
    tasks = [run_safe_task(value, interval, queue) for value in values]
    await asyncio.gather(*tasks)





if __name__ == "__main__":
    initialize_settings()
    asyncio.run(main())
