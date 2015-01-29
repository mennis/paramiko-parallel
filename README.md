# paramiko-parallel

a non-blocking cmd object :

<pre>
    c = Cmd(user, hostname, password, command, port=22)
    c.run()
    # do other things
    c.wait() # to block or use an 'if not c.done:' control struct
    c.result.status
    c.result.message
</pre>

When the remote job has completed it will set:

<pre>
    .done to True
    .message to a NamedTuple that can be sliced or
        referenced by name:

            status or 0: exitcode as int
            stdout or 1: stdout as str
            stderr or 2: stderr as str

    .status with the exit code as a boolean
</pre>

and try to store the json data as a dict in .dict .
