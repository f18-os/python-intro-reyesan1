#! /usr/bin/env python3

import fileinput
import os, sys, time, re
def pipeCall(args, i):
    # Setting new file descriptors, read and write
    args1 = args[:(i-1)]
    args2 = args[i:]

    pr,pw = os.pipe()
    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        os.close(1)                 # redirect child's stdout
        os.dup(pw)
        for fd in (pr, pw):
            os.close(fd)
        fd = sys.stdout.fileno() # os.open(myFile, os.O_CREAT)
        os.set_inheritable(fd, True)
        
        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args1[0])
            try:
                os.execve(program, args1, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 


    lc = os.fork()

    if lc < 0:
        sys.exit(1)

    elif lc == 0:                   #  child - will write to pipe
        os.close(0)                 # redirect child's stdout
        os.dup(pr)
        for fd in (pr, pw):
            os.close(fd)
        fd = sys.stdin.fileno() # os.open(myFile, os.O_CREAT)
        os.set_inheritable(fd, True)

        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args2[0])
            try:
                os.execve(program, args2, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 
           
    else:                           # parent (forked ok)
        #os.close(0)
        childPidCode = os.wait()
        os.dup(pr)
        for fd in (pw, pr):
            os.close(fd)
    
def redirectCall(args):
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                   # child
        sys.stdout = open(args[index], "w")
        fd = sys.stdout.fileno() # os.open(myFile, os.O_CREAT)
        os.set_inheritable(fd, True)
        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 

        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        childPidCode = os.wait()

usrInput = ""
while usrInput != "exit":
        usrInput = input("$ ")
        if usrInput.strip() == "exit":
            sys.exit(0) 
        if usrInput[:2] == "cd":
            os.chdir(usrInput[3:])
            continue

        pid = os.getpid()               # get and remember pid
        args = usrInput.split()
        redirect = False
        pipe = False
        index = 0
        for a in args:
            index += 1
            if a == '>':
                redirect = True
                os.close(1)                 # redirect child's stdout
                redirectCall(args)
                break
            if a == '|':
                pipe = True
                pipeCall(args, index)
                break

#        os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
        if not pipe and not redirect:
            rc = os.fork()

            if rc < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

            elif rc == 0:                   # child
                for dir in re.split(":", os.environ['PATH']): # try each directory in path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 

                os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error

            else:                           # parent (forked ok)
                childPidCode = os.wait()
