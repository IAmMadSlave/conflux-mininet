#!/usr/bin/python

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

    def __str__( self ):
        out = 'pid: {}\n'.format( self.pid )
        for fd in self.fds:
            out += '\tfd: {}\n\tdest_ip: {}\n\tdest_port: {}\n'.format( fd['fd'], fd['dest_ip'], fd['dest_port'] )
        return out
