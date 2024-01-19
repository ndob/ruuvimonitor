import argparse
from multiprocessing import Process
import signal

from collector import run_collector
from db import init_db
from webui import run_webui

DATABASE_NAME = "readings.db"

g_procs = []

def sigterm_handler(signum, frame):
    print(f"Got signal: {signum}")
    for p in g_procs:
        p.terminate()
        p.kill()
        print("Term called")

def main():
    global g_procs

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--update-interval", type=int, default=60, help="Interval in seconds for sensor reading updates.")
    parser.add_argument("-u", "--disable-ui", action="store_true", default=False)
    parser.add_argument("-c", "--disable-collector", action="store_true", default=False)

    args = parser.parse_args()

    # Init signal handler so we can kill child processes.
    signal.signal(signal.SIGTERM, sigterm_handler)

    # Create (and migrate if necessary) the db.
    init_db(DATABASE_NAME)

    if not args.disable_collector:
        p = Process(target=run_collector, args=(DATABASE_NAME, args.update_interval,))
        p.start()
        g_procs.append(p)

    if not args.disable_ui:
        p = Process(target=run_webui, args=(DATABASE_NAME,))
        p.start()
        g_procs.append(p)

    for p in g_procs:
        p.join()

    print("Quit.")

if __name__ == '__main__':
    main()