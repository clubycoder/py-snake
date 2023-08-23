f = open("log.txt", "a")

FILENAME = "log.txt"


def log(msg):
    with open(FILENAME, "a") as f:
        f.write(msg + "\n")
