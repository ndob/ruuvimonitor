import argparse
from multiprocessing import Process
from collector import run_collector
from webui import run_webui

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--update-interval", type=int, default=60, help="Interval in seconds for sensor reading updates.")
    parser.add_argument("-u", "--disable-ui", action="store_true", default=False)
    parser.add_argument("-c", "--disable-collector", action="store_true", default=False)

    args = parser.parse_args()

    procs = []
    if not args.disable_collector:
        p = Process(target=run_collector, args=(args.update_interval,))
        p.start()
        procs.append(p)

    if not args.disable_ui:
        p = Process(target=run_webui)
        p.start()
        procs.append(p)

    # TODO: Fix. Currently blocks forever here.
    for p in procs:
        p.join()
