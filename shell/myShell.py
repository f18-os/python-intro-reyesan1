#! /usr/bin/env python3

import fileinput
import os, sys, time, re

# Function for when pipe is called
def pipeCall(args, i):

    # Getting left and right pipe arguments
    args1 = args[:(i-1)]
    args2 = args[i:]

    # Setting new file descriptors, read and write
    pr,pw = os.pipe()

    # Forking left child of pipe
    lc = os.fork()
    
    if lc < 0:
        sys.exit(1)

    elif lc == 0:                   #  child - will write to pipe
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

    # Forking right child of pipe
    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
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
        childPidCode = os.wait()
        os.dup(pr)
        for fd in (pw, pr):
            os.close(fd)

# Redirecting Function
def redirectCall(args, index, direction):
    rc = os.fork()
   
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                  # child
        # If output redirection
        if direction == "out":
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(args[-1], "w+")
            fd = sys.stdout.fileno() # os.open(myFile, os.O_CREAT)
            os.set_inheritable(fd, True)
        # If input redirection
        elif direction == "in":
            os.close(0)                 # redirect child's stdout
            sys.stdin = open(args[-1], "r")
            fd = sys.stdin.fileno() # os.open(myFile, os.O_CREAT)
            os.set_inheritable(fd, True)
        del args[-1]

        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 

        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        if not sleep: 
            childPidCode = os.wait()

usrInput = ""
while usrInput != "exit":
    # Try for EOF
    try:
        prompt = "shell$>"
        # Getting PS1
        if 'PS1' in os.environ:
            prompt = os.environ['PS1']

        usrInput = input("%s" % prompt)

        # Checking if user wants to exit
        if usrInput.strip() == "exit":
            sys.exit(0)
        # If user input is cd 
        if usrInput[:2] == "cd":
            # If user wants to go back one directory
            if usrInput[3:].strip() == "..":
                # Getting current directory
                curr = os.getcwd()
                # Spliting at each directory
                curr = curr.split("/")
                # Deleting the last directory
                del curr[-1]
                # Joining them back as a string without last directory
                path= '/'.join(curr)
                # Going to previous directory
                os.chdir(path)
            else: 
                # Going to regular directory path
                os.chdir(usrInput[3:])
            continue

        pid = os.getpid()               # get and remember pid

        # Splittin input into array
        args = usrInput.split()
        # Sleep flag for call
        sleep = False
        # If sleep call found
        if '&' in usrInput:
            sleep = True
            find = 0
            # Removing & if found
            for u in args:
                if u == '&':
                    del args[find]
                find +=1
        # Redirect and pipe flags
        redirect = False
        pipe = False
        # Finding index of operators
        index = 0
        for a in args:
            index += 1
            if a == '>':
                redirect = True
                del args[(index-1)]
                redirectCall(args, index, "out")
                continue
                break
            if a == '|':
                pipe = True
                pipeCall(args, index)
                continue
                break
            if a == '<':
                redirect = True
                del args[(index-1)]
                redirectCall(args, index, "in")
                continue
                break
        # If no inputs
        if not pipe and not redirect:
            # If full path command entered
            if usrInput[0] == "/":
                program = args[0]
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            # For general commands
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
                if not sleep:
                    childPidCode = os.wait()
    except EOFError:
        sys.exit(0)
