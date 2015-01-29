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
    .message with the dict version of the fio output
    .status with the exit code as a boolean
</pre>

and try to store the json data as a dict in .dict .
