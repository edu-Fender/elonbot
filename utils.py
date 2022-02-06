from datetime import datetime


def log(*params):
    print(datetime.now(), flush=True, *params)
    with open("output.log", 'a') as f:
        f.write("{} {}".format(datetime.now(), *params))
        f.flush()
