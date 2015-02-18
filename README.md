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

Currently stderr and stdout is pinned at a max of 1,000,000 characters. Each command run 
will allocate this 2MB in buffers for temporary storage.  I'd like to fix this but I'm not
sure how best to do that while allowing the child to populate the parent.
