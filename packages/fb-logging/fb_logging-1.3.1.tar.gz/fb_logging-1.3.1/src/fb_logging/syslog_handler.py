#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: A wrapping logging handler for logging.handlers.SysLogHandler.

It's intended to convert all log messages to utf-8.
"""

# Standard modules
import errno
import os
import socket
import stat
import sys
from logging.handlers import SYSLOG_UDP_PORT
from logging.handlers import SysLogHandler

__version__ = "0.3.3"

if sys.version_info[0] < 3:
    raise RuntimeError("This module may only be used with Python > 3.1.")
if sys.version_info[0] == 3 and sys.version_info[1] <= 1:
    raise RuntimeError("This module may only be used with Python > 3.1")


# =============================================================================
class FbSysLogHandler(SysLogHandler):
    """A wrapper logging handler for logging.handlers.SysLogHandler.

    It's intended to convert all log messages to utf-8.
    """

    def __init__(
        self,
        address=("localhost", SYSLOG_UDP_PORT),
        facility=SysLogHandler.LOG_USER,
        socktype=None,
        encoding="utf-8",
    ):
        """Initialize the FbSysLogHandler.

        To log to a local syslogd, `FbSysLogHandler(address="/dev/log")`
        may be used.

        If facility is not specified, LOG_USER is used.

        @param address: either the network socket of the syslog daemon
                        (if given as tuple) or the filename of the UNIX socket
                        of the syslog daemon (if given as str).
        @type address: tuple or str
        @param facility: syslog facility to use
        @type facility: int
        @param socktype: the socket type (socket.SOCK_DGRAM or socket.SOCK_STREAM) to use.
        @type socktype: int
        @param encoding: the character set to use to decode byte messages
        @type encoding: str

        """
        # Initialisation of the parent object
        do_ux_socket = False

        if isinstance(address, str):
            if not os.path.exists(address):
                raise OSError(errno.ENOENT, "File doesn't exists", address)
            mode = os.stat(address).st_mode
            if not stat.S_ISSOCK(mode):
                raise OSError(errno.EPERM, "File is not a UNIX socket file", address)
            if not os.access(address, os.W_OK):
                raise OSError(errno.EPERM, "No write access to socket", address)

            do_ux_socket = True

        if do_ux_socket:
            SysLogHandler.__init__(self, address, facility, None)
        else:
            SysLogHandler.__init__(self, address, facility, socktype)

        self.encoding = encoding
        """
        @ivar: the character set to use to decode byte messages
        @type: str
        """

    # -------------------------------------------------------------------------
    def _connect_unixsocket(self, address):

        use_socktype = getattr(self, "socktype", None)

        if use_socktype is None:
            use_socktype = socket.SOCK_DGRAM

        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        try:
            self.socket.connect(address)
            # it worked, so set self.socktype to the used type
            self.socktype = use_socktype
        except socket.error:
            self.socket.close()
            if self.socktype is not None:
                # user didn't specify falling back, so fail
                raise
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            try:
                self.socket.connect(address)
                # it worked, so set self.socktype to the used type
                self.socktype = use_socktype
            except socket.error:
                self.socket.close()
                raise

    # -------------------------------------------------------------------------
    def emit(self, record):
        """Wrap for SysLogHandler.emit().                           # noqa: D402.

        Encode an unicode message to UTF-8 (or whatever).
        """
        msg = record.msg
        if isinstance(msg, bytes):
            msg = msg.decode(self.encoding)
            record.msg = msg

        SysLogHandler.emit(self, record)


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
