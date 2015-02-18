from paramiko import SSHClient
from multiprocessing import Process, Value, Array
from collections import namedtuple
import logging
import time
import paramiko

logger = logging.getLogger()
logger.setLevel(logging.INFO)

Dformatter = logging.Formatter('%(asctime)s %(message)s')
Vformatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(Dformatter)

logger.addHandler(console)

Data = namedtuple('Data', ['status', 'stdout', 'stderr'], verbose=False)


class AllowAnythingPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return


class Cmd(object):
    """
    a non-blocking cmd object ::

        c = Cmd(init, params)
        c.run()
        # do other things
        c.wait() # or use an 'if not c.done:' control struct
        c.result.status
        c.result.message

    When the remote job has completed it will set::

        .done to True
        .message with the dict version of the fio output
        .status with the exit code as a boolean

    and try to store the json data as a dict in .dict .

    """

    def __init__(self, user, hostname, password, command, port=22):

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.command = command
        self.time = float()
        self.started = False
        self.__status = Value('i')
        self.__stdout = Array('c', 1000000)
        self.__stderr = Array('c', 1000000)
        self.p = None
        self.user = user
        self.hostname = hostname
        self.password = password
        self.port = port

    @staticmethod
    def _read(channelobj):
        """
        read until EOF
        """
        buf = channelobj.readline()
        output = str(buf)
        while buf:
            buf = channelobj.readline()
            output += buf
        return output

    def _runcmd(self, status, stdout, stderr):
        """
        this private method is executed as a thread

        :type status: c_int representing a bool
        :type stdout: c_array of char
        :type stderr: c_array of char
        """

        self.started = True
        start = time.time()
        self.client.connect(self.hostname, self.port, self.user, self.password)
        stdin, sout, serr = self.client.exec_command(self.command)
        err = serr.read()
        for i in range(len(err)):
            stderr[i] = str(err[i])

        # we must read stderr _before_ stdout
        # otherwise paramiko was losing the stdout data
        status = sout.channel.recv_exit_status()
        out = sout.read()
        status += int(status)

        # copy stdout into shared memory
        for i in range(len(out)):
            stdout[i] = str(out[i])
        self.client.close()
        self.time = time.time() - start

    def wait(self):
        """
        This is basicaly join.  It blocks untill the job is done.
        :rtype: NamedTuple
        """
        then = time.time()
        while not self.done:
            time.sleep(.01)
        else:
            logger.debug("waited for {:10.4f} sec".format(time.time() - then))
        return self.result

    def run(self):
        """
        start the job on the remote host
        """
        self.p = Process(target=self._runcmd, args=(self.__status, self.__stdout, self.__stderr))
        self.p.start()
        while not self.p.is_alive():
            time.sleep(.1)
            logger.debug("slept not started")
        else:
            self.started = True

    @property
    def done(self):
        """
        :return: whether or not the job is complete
        :rtype: bool
        """
        if self.started and not self.p.is_alive():
            return True
        else:
            return False

    @property
    def result(self):
        """
        Return the result as a NamedTuple this means that result can be sliced or
        referenced by name:

            status or 0: exitcode as int
            stdout or 1: stdout as str
            stderr or 2: stderr as str

        so upon completion the following:

            cmd.result[0]
            cmd.status

        are equivilent. *If the process is not complete this will block.*
        """
        if not self.done:
            self.wait()
        else:
            return Data(self.__status.value, str(self.__stdout.value), str(self.__stderr.value))
