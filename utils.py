from datetime import datetime


def log(*params):

    now = datetime.now()

    string = ''
    for i in params:
        if type(i) is not str:
            i = str(i)
        string += i + ' '

    print(now, string, flush=True)

    with open(f"log/output-{now.date()}.log", 'a') as f:
        f.write("{} {}\n".format(now, string))
