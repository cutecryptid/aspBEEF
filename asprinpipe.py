import sys
from subprocess import PIPE, Popen
from threading  import Thread


if __name__ == "__main__":
    asprinargs = sys.argv[1:]
    command = ["asprin"] + asprinargs
    #command = ["python"] + asprinargs

    process = Popen(command, stdout=PIPE, stderr=PIPE)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        print(line)





