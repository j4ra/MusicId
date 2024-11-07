import os
import subprocess
from croniter import croniter
from datetime import datetime
import time

def main():
    cron = os.getenv("cron", "0 */12 * * *")
    rate_limit = os.getenv("rate", 4)

    print("Starting the server with parameters:")
    print(f"\t cron : {cron}")
    print(f"\t frequency: {rate_limit} per minute")
    print ("running...")

    res = subprocess.run(["python3", "/script/main.py"]).returncode
    if res != 0:
        print("stopping")
        return

    start_time = datetime.now()
    iter = croniter(cron, start_time)
    next_time = iter.get_next(datetime)

    while(True):
        if (datetime.now() > next_time):
            next_time = iter.get_next(datetime)
            if subprocess.run(["python3", "/script/main.py"]).returncode != 0:
                print("stopping")
                return

        time.sleep(15)

if __name__ == '__main__':
    main()