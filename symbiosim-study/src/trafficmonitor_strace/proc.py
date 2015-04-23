#!/usr/bin/python

from re import match
from subprocess import Popen, PIPE

class procinfofactory():
    def __init__( self ):
        self.procs = []
        return

    def get_proc( self, pid ):
        for proc in self.procs:
            if proc.pid == int(pid):
                return proc
        else:
            proc = procinfo( pid )
            self.procs.append( proc )
            return proc

class procinfo():
    def __init__( self, pid ):
        self.pid = int(pid)
        self.fds = []

    def add_fd( self, fd, dest_ip, port ):
        tcp_info = { 'fd': int(fd),
                     'dest_ip': dest_ip,
                     'dest_port': int(port) }

        self.fds.append( tcp_info )

    def is_socket( self, fd ):
        path = '/proc/{}/fd/{}'.format( self.pid, fd )
        p = Popen( ['sudo', 'ls', '-l', path], stdout=PIPE, stderr=PIPE )
        if not p.stderr.read():
            for line in p.stdout.readlines():
                line = line.strip('\n').split()
                # pull out inode looks something like socket:[1234]
                if match( 'socket', line[-1] ):
                    line = line[-1].split( ':' )
                    return  line[-1].translate( None, '[]' )

        return None

    def __str__( self ):
        out = 'pid: {}\n'.format( self.pid )
        for fd in self.fds:
            out += '\tfd: {}\n\tdest_ip: {}\n\tdest_port: {}\n'.format( fd['fd'], fd['dest_ip'], fd['dest_port'] )
        return out

if __name__ == '__main__':
    pif = procinfofactory()
    proc = pif.get_proc( '18549' )
    print proc.is_socket( '3' )
