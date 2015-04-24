#!/usr/bin/python

import os
import shlex
from re import match
from subprocess import Popen, PIPE

from mininet.net import Mininet
from mininet.node import Host

class procinfofactory():
    def __init__( self, host, mn_pipes_table ):
        self.host = host
        self.mn_pipes_table = mn_pipes_table
        self.procs = []
        return

    def add_proc( self, pid ):
        for proc in self.procs:
            if proc.pid == int(pid):
                return proc
        else:
            proc = procinfo( pid, self.host, self.mn_pipes_table )
            self.procs.append( proc )
            return proc

class procinfo():
    def __init__( self, pid, host, mn_pipes_table ):
        self.pid = int(pid)
        self.host = host
        self.mn_pipes_table = mn_pipes_table
        self.fds = []

    def add_fd( self, fd ):
        for f in self.fds:
            if fd == f['fd']:
                return f['name']
        else:
            inode = self.is_socket( fd )
            if inode:
                # use inode to get pipe

                fd_info = { 'name': None,
                            'fd': fd }
                self.fds.add( fd_info )
                return fd_info['name']
            else:
                return None

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

    def inode_to_pipe( self, inode ):
        env = os.environ.copy()
        cmd = ['cat', '/proc/net/tcp']
        cat = host.popen( cmd, env=env, stdout=PIPE, stderr=PIPE )
        cat.wait()
        cmd = "awk '{if (NR!=1) {print $3, $10}}'"
        cmd = shlex.split( cmd )
        awk = host.popen( cmd, env, stdin=cat.stdout, stdout=PIPE, stderr=PIPE )
        for line in awk.stdout.readlines():
            line = line.split()
            if line[-1].strip( '\n' ) == inode:
                line = line[0].split( ':' )[0]
                dest_ip = [dest_ip[i:i+2] for i in range(0, len(dest_ip), 2)]
                dest_ip = [str(int(x, 16)) for x in dest_ip]
                dest_ip = dest_ip[::-1]
                dest_ip = '.'.join( dest_ip )

                return dest_ip

        return None

    def __str__( self ):
        out = 'pid: {}\n'.format( self.pid )
        for fd in self.fds:
            out += '\tfd: {}\n\tdest_ip: {}\n\tdest_port: {}\n'.format( fd['fd'], fd['dest_ip'], fd['dest_port'] )
        return out

if __name__ == '__main__':
    pif = procinfofactory()
    proc = pif.add_proc( '18549' )
    print proc.is_socket( '3' )
