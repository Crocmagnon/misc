import datetime
import re
import subprocess

DISK_SIZE_GB = 5.44


def sizeof_fmt(num: int, suffix: str = 'B') -> str:
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def time_fmt(_time):
    hours = int(_time / 3600)
    minutes = int((_time % 3600) / 60)
    seconds = _time % 60
    fmt = f"{hours}h {minutes}min {seconds}s"
    return fmt


def main():
    subprocess.run(["sudo", "killall", "-SIGINFO", "dd"])
    print("Input last dd progress line")
    last_line = input("> ")
    regex = re.compile(
        r"^(?P<transferred>\d+) \w+ transferred in (?P<elapsed>\d+).\d+ secs \((?P<speed>\d+) \w+/sec\)$")
    results = regex.match(last_line).groupdict()

    disk_size = DISK_SIZE_GB * 1024 * 1024 * 1024

    transferred = int(results["transferred"])
    transferred_fmt = sizeof_fmt(transferred)
    speed = int(results["speed"])
    speed_fmt = sizeof_fmt(speed)
    remaining = disk_size - transferred
    remaining_fmt = sizeof_fmt(remaining)

    eta = int(remaining / speed)
    eta_fmt = time_fmt(eta)
    elapsed = int(results["elapsed"])
    elapsed_fmt = time_fmt(elapsed)
    total = eta + elapsed
    total_fmt = time_fmt(total)

    eta_absolute = datetime.datetime.now() + datetime.timedelta(seconds=eta)

    percentage = transferred / disk_size * 100

    print()
    print(f"{transferred_fmt} transferred over {DISK_SIZE_GB}GiB, or {percentage:.1f}%.")
    print(f"Transferring at {speed_fmt} per second.")
    print(f"Remaining : {remaining_fmt}")
    print(f"ETA : {eta_fmt} ({eta_absolute.ctime()}).")
    print(f"Elapsed : {elapsed_fmt}.")
    print(f"Estimated total time : {total_fmt}.")


if __name__ == '__main__':
    main()
