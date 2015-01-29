from unittest import TestCase
import time
from parallelCmd import Cmd
import vagrant
import paramiko

paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)


class TestCmd(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vm = vagrant.Vagrant()
        cls.vm.up()
        c = cls.vm.conf()
        cls.ip = c.get('HostName')
        cls.port = c.get('Port')
        cls.password = 'vagrant'
        cls.user = 'vagrant'
        cls.many = 100

    @classmethod
    def tearDownClass(cls):
        cls.vm = vagrant.Vagrant()
        cls.vm.destroy()

    def test_paramiko_works(self):
        cmd = Cmd(self.user, self.ip, self.password,  'uname', int(self.port))
        cmd.client.connect(cmd.hostname, cmd.port, cmd.user, cmd.password)
        self.assertEqual(cmd.client.exec_command('uname')[1].read().strip(), 'SunOS')

    def test_run(self):
        cmd = Cmd(self.user, self.ip, self.password,  'uname', int(self.port))
        cmd.run()
        while not cmd.done:
            time.sleep(1)

        self.assertEqual(cmd.result[1].strip(), 'SunOS')

    def test_ManyConnections(self):
        connections = []
        for x in range(10):
            connections.append(Cmd(self.user, self.ip, self.password,  'cat /usr/dict/words', int(self.port)))

        for cmd in connections:
            cmd.run()

        while False in [cmd.done for cmd in connections]:
            time.sleep(.01)

        for cmd in connections:
            self.assertEqual(len(cmd.result[1]), 206695)  # TODO: calculate size then check against that
