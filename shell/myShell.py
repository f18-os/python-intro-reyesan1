#! /usr/bin/env python3

import os, sys, time, re

os.write(1, ("Hello, welcome to the shell.\n").encode())
usrInput = ""
while usrInput != "exit":
        usrInput = input("$ ")
        if usrInput.strip() == "exit":
            os.write(1, ("Shell terminated with exit code 0\n").encode())
            sys.exit(0) 

        pid = os.getpid()               # get and remember pid

        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:                   # child
            # Splitting user input into argument array
            args = usrInput.split()

            # Redirect and pipe start at false
            redirect = False
            pipe = False  
            # Variable to track where redirect file is located
            i = 0
            
            # Loopping through arguments to find if there is a '>'
            for a in args:
                # Incrementing until '>' is found
                i += 1
                # If '>' is found, track index and redirect is true, close file descriptor
                if a == '>':
                    redirect = True
                    os.close(1)                 
                    break

                # If '|' is found, track index and redirect is true, close file descriptor
                if a == '|':
                    pipe = True
                    break
            
            # If redirect is true, open/create file  
            if redirect:
                sys.stdout = open(args[i], "w+")
                # os.open(myFile, os.O_CREAT)
                fd = sys.stdout.fileno() 
                os.set_inheritable(fd, True)
                # Getting rid of redirected file and '>' from arguments
                del args[i-1] 
                del args[-1]
            
            if pipe:
                # Setting new file descriptors, read and write
                pr,pw = os.pipe()
                # Setting file descriptors as inheritable
                for f in (pr, pw):
                    os.set_inheritable(f, True)
                   
            # Try each directory in path
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, args[0])
                try:
                    # Try to exec program
                    os.execve(program, args, os.environ)
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

        else:                           # parent (forked ok)
#            os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
#                         (pid, rc)).encode())
            childPidCode = os.wait()
#            os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
#                         childPidCode).encode())
