import subprocess

def asked_for_help(args):
    if len(args)>=1:
        return ('--help' in args) or (len(args)>=1 and args[0]=='help') or (len(args)>=2 and args[1]=='help')

def show_help():
    subprocess.call(['man', 'puree'])
