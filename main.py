
import argparse
import threading
import time

import psutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


def has_enough_mem(required_gb):
    return psutil.virtual_memory().available > required_gb * 1024**3


def browser_worker(sid, url, min_mem_gb):
    while True:
        driver = None
        try:
            if not has_enough_mem(min_mem_gb):
                print(f"session {sid} waiting for memory...")
                time.sleep(10)
                continue

            print(f"starting session {sid} for {url}")

            opts = Options()
            args = [
                "--headless=new", "--disable-gpu", "--no-sandbox",
                "--disable-dev-shm-usage", "--disable-software-rasterizer",
                "--disable-background-networking", "--disable-default-apps",
                "--disable-extensions", "--disable-sync", "--disable-translate",
                "--disable-notifications", "--mute-audio", "--window-size=640,360",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-background-timer-throttling",
                "--disable-features=ScriptStreaming",
                "--renderer-process-limit=1", "--max-old-space-size=128",
                "--log-level=3", "--disable-logging"
            ]
            for arg in args:
                opts.add_argument(arg)

            opts.add_experimental_option(
                "excludeSwitches", ["enable-automation", "enable-logging"]
            )
            opts.add_experimental_option('useAutomationExtension', False)
            opts.add_argument('--blink-settings=imagesEnabled=false')

            driver = webdriver.Chrome(options=opts)
            driver.set_page_load_timeout(30)
            driver.get(url)

            mem_free = psutil.virtual_memory().available // 1024**2
            print(f"session {sid} started, mem_free: {mem_free}MB")

            refresh_count = 0
            while True:
                time.sleep(1 + (refresh_count % 10) * 0.1)
                try:
                    driver.refresh()
                    refresh_count += 1

                    if refresh_count % 100 == 0:
                        mem_free = psutil.virtual_memory().available // 1024**2
                        print(
                            f"session {sid}: {refresh_count} refreshes, "
                            f"mem_free: {mem_free}MB"
                        )

                except WebDriverException as e:
                    if "target window closed" in str(e).lower():
                        print(f"session {sid} window closed, restarting.")
                        break
                    print(f"session {sid} refresh failed: {e.__class__.__name__}")
                    time.sleep(3)

        except Exception as e:
            print(
                f"critical error in session {sid}: "
                f"{e.__class__.__name__}. restarting in 10s."
            )
        finally:
            if driver:
                try:
                    driver.quit()
                except WebDriverException:
                    pass
            time.sleep(10)


def main():
    """Main function to parse arguments and start browser workers."""
    parser = argparse.ArgumentParser(description="Sidekick View Booster")
    parser.add_argument("-u", "--url", type=str, required=True, help="Target URL")
    parser.add_argument(
        "-n", "--browsers", type=int, default=2, help="Number of browser instances"
    )
    parser.add_argument(
        "-m", "--min-mem", type=int, default=2, help="Min free RAM in GB to launch"
    )
    args = parser.parse_args()

    for i in range(args.browsers):
        sid = i + 1
        while not has_enough_mem(args.min_mem):
            print(f"waiting for {args.min_mem}GB RAM to launch session {sid}...")
            time.sleep(15)

        thread = threading.Thread(
            target=browser_worker,
            args=(sid, args.url, args.min_mem),
            daemon=True
        )
        thread.start()
        print(f"launched {sid}/{args.browsers}")
        if i < args.browsers - 1:
            time.sleep(5)

    print("all threads launched. press ctrl+c to exit.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nexiting.")


if __name__ == "__main__":
    main()
