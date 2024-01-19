import argparse
from threading import Thread
import signal

from collector import run_collector
from db import init_db
from webui import run_webui

DATABASE_NAME = "readings.db"

def main():
    threads = []

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--update-interval", type=int, default=60, help="Interval in seconds for sensor reading updates.")
    parser.add_argument("-u", "--disable-ui", action="store_true", default=False)
    parser.add_argument("-c", "--disable-collector", action="store_true", default=False)

    args = parser.parse_args()

    # Create (and migrate if necessary) the db.
    init_db(DATABASE_NAME)

    if not args.disable_collector:
        t = Thread(target=run_collector, args=(DATABASE_NAME, args.update_interval,))
        t.start()
        threads.append(t)

    if not args.disable_ui:
        t = Thread(target=run_webui, args=(DATABASE_NAME,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Quit.")

if __name__ == '__main__':
    main()