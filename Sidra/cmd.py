from subprocess import PIPE, Popen

def cmd(command):
    return Popen(args=command, stdout=PIPE, shell=True).communicate()[0]
