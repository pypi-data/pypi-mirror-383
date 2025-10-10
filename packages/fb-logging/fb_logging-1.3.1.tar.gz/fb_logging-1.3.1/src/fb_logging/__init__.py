#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Python modules to extend the logging mechanism in Python.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""

__author__ = "Frank Brehm <frank@brehm-online.com>"
__copyright__ = "(C) 2025 by Frank Brehm, Berlin"
__contact__ = "frank@brehm-online.com"
__version__ = "1.3.1"
__license__ = "LGPL-3"

# Standard modules
import copy
import logging
import logging.handlers
import os
import syslog
from numbers import Number

TRACE = 5
DEBUG = logging.DEBUG
INFO = logging.INFO
NOTICE = 25
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


# =============================================================================
class FbLoggingError(Exception):
    """Base error class for all other self defined exceptions."""

    pass


# =============================================================================
class SyslogFacitityError(FbLoggingError):
    """Base error class for exceptions in class FbSyslogFacilityInfo."""

    pass


# =============================================================================
class WrongLogFacilityIdTypeError(SyslogFacitityError, TypeError):
    """Error class about a wrong variable type as a Syslog facility Id.

    Special error class for the case, a wrong variable type (instead of Integer)
    was tried to use as a Syslog facility id.
    """

    # -------------------------------------------------------------------------
    def __init__(self, value):
        """Construct this exception."""
        self.value = value

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        msg = "Wrong variable {v!r} ({t}) given as a syslog facility id.".format(
            v=self.value, t=self.value.__class__.__name__
        )
        return msg


# =============================================================================
class WrongLogFacilityIdValueError(SyslogFacitityError, ValueError):
    """Error class about a wrong variable value as a Syslog facility Id.

    Special error class for the case, a wrong variable value was tried to use
    as a Syslog facility id.
    """

    # -------------------------------------------------------------------------
    def __init__(self, value):
        """Construct this exception."""
        self.value = value

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        msg = "Wrong variable {} given as a syslog facility id.".format(self.value)
        return msg


# =============================================================================
class WrongLogFacilityNameTypeError(SyslogFacitityError, TypeError):
    """Error class about a wrong variable type as a Syslog facility name.

    Special error class for the case, a wrong variable type (instead of String)
    was tried to use as a Syslog facility name.
    """

    # -------------------------------------------------------------------------
    def __init__(self, value):
        """Construct this exception."""
        self.value = value

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        msg = "Wrong variable {v!r} ({t}) given as a syslog facility name.".format(
            v=self.value, t=self.value.__class__.__name__
        )
        return msg


# =============================================================================
class WrongLogFacilityNameValueError(SyslogFacitityError, ValueError):
    """Error class about a wrong variable value as a Syslog facility name.

    Special error class for the case, a wrong variable value was tried to use
    as a Syslog facility name.
    """

    # -------------------------------------------------------------------------
    def __init__(self, value):
        """Construct this exception."""
        self.value = value

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        msg = "Wrong variable {!r} given as a syslog facility name.".format(self.value)
        return msg


# =============================================================================
def stdout_is_redirected():
    """Check if stdout is redirected."""
    return os.fstat(0) != os.fstat(1)


# =============================================================================
def stderr_is_redirected():
    """Check if stderr is redirected."""
    return os.fstat(0) != os.fstat(2)


# =============================================================================
def use_unix_syslog_handler():
    """Use UnixSyslogHandler for logging instead of SyslogHandler.

    @return: using UnixSyslogHandler
    @rtype: bool
    """
    use_syslog = False
    un = os.uname()
    os_name = un[0].lower()
    if os_name == "sunos":
        use_syslog = True

    return use_syslog


# =============================================================================
class FbSyslogFacilityInfo(object):
    """Inform about Syslog facilities.

    A pure information class about Syslog facilities, their names and their
    numeric representation.

    This class does not need an instantiation, because it consists only from
    class members and class methods.
    """

    syslog_facilities = {}
    syslog_facility_names = {}

    if use_unix_syslog_handler():
        syslog_facilities = {
            "auth": syslog.LOG_AUTH,
            "cron": syslog.LOG_CRON,
            "daemon": syslog.LOG_DAEMON,
            "kern": syslog.LOG_KERN,
            "local0": syslog.LOG_LOCAL0,
            "local1": syslog.LOG_LOCAL1,
            "local2": syslog.LOG_LOCAL2,
            "local3": syslog.LOG_LOCAL3,
            "local4": syslog.LOG_LOCAL4,
            "local5": syslog.LOG_LOCAL5,
            "local6": syslog.LOG_LOCAL6,
            "local7": syslog.LOG_LOCAL7,
            "lpr": syslog.LOG_LPR,
            "mail": syslog.LOG_MAIL,
            "news": syslog.LOG_NEWS,
            "user": syslog.LOG_USER,
            "uucp": syslog.LOG_UUCP,
        }
    else:
        syslog_facilities = {
            "auth": logging.handlers.SysLogHandler.LOG_AUTH,
            "authpriv": logging.handlers.SysLogHandler.LOG_AUTHPRIV,
            "cron": logging.handlers.SysLogHandler.LOG_CRON,
            "daemon": logging.handlers.SysLogHandler.LOG_DAEMON,
            "kern": logging.handlers.SysLogHandler.LOG_KERN,
            "local0": logging.handlers.SysLogHandler.LOG_LOCAL0,
            "local1": logging.handlers.SysLogHandler.LOG_LOCAL1,
            "local2": logging.handlers.SysLogHandler.LOG_LOCAL2,
            "local3": logging.handlers.SysLogHandler.LOG_LOCAL3,
            "local4": logging.handlers.SysLogHandler.LOG_LOCAL4,
            "local5": logging.handlers.SysLogHandler.LOG_LOCAL5,
            "local6": logging.handlers.SysLogHandler.LOG_LOCAL6,
            "local7": logging.handlers.SysLogHandler.LOG_LOCAL7,
            "lpr": logging.handlers.SysLogHandler.LOG_LPR,
            "mail": logging.handlers.SysLogHandler.LOG_MAIL,
            "news": logging.handlers.SysLogHandler.LOG_NEWS,
            "syslog": logging.handlers.SysLogHandler.LOG_SYSLOG,
            "user": logging.handlers.SysLogHandler.LOG_USER,
            "uucp": logging.handlers.SysLogHandler.LOG_UUCP,
        }

    for facility_name in syslog_facilities.keys():
        facility_id = syslog_facilities[facility_name]
        syslog_facility_names[facility_id] = facility_name

    raise_on_wrong_facility_name = True

    # -------------------------------------------------------------------------
    @classmethod
    def facility_id(cls, value):
        """Tryi to get the numeric syslog facility Id for the given facility name.

        @raises WrongLogFacilityNameTypeError, if the given value
                has the wrong variable type
        @raises WrongLogFacilityNameValueError, if the given value
                was not found.

        @return: numeric syslog facility id
        @rtype: int
        """
        if not isinstance(value, str):
            raise WrongLogFacilityNameTypeError(value)

        val = value.lower()

        if val not in cls.syslog_facilities:
            if cls.raise_on_wrong_facility_name:
                raise WrongLogFacilityNameValueError(value)
            else:
                return None

        return cls.syslog_facilities[val]

    # -------------------------------------------------------------------------
    @classmethod
    def facility_name(cls, value):
        """Try to get the syslog facility name for the given facility Id.

        @raises WrongLogFacilityIdTypeError, if the given value
                has the wrong variable type
        @raises WrongLogFacilityIdValueError, if the value
                was not found.

        @return: syslog facility name
        @rtype: str
        """
        if not isinstance(value, Number):
            raise WrongLogFacilityIdTypeError(value)

        val = int(value)
        if val != value:
            if cls.raise_on_wrong_facility_name:
                raise WrongLogFacilityIdValueError(value)
            else:
                return None

        if val not in cls.syslog_facility_names:
            if cls.raise_on_wrong_facility_name:
                raise WrongLogFacilityIdValueError(value)
            else:
                return None

        return cls.syslog_facility_names[val]


# =============================================================================
def valid_syslog_facilities():
    """Return a copy of FbSyslogFacilityInfo.syslog_facilities."""
    return copy.copy(FbSyslogFacilityInfo.syslog_facilities)


# =============================================================================
def syslog_facility_names():
    """Return a copy of FbSyslogFacilityInfo.syslog_facility_names."""
    return copy.copy(FbSyslogFacilityInfo.syslog_facility_names)


# =============================================================================
def get_syslog_facility_name(syslog_facility):
    """Wrap the FbSyslogFacilityInfo.facility_name()."""
    return FbSyslogFacilityInfo.facility_name(syslog_facility)


# =============================================================================
def syslog_facility_name(syslog_facility):
    """Wrap the FbSyslogFacilityInfo.facility_name()."""
    return FbSyslogFacilityInfo.facility_name(syslog_facility)


# =============================================================================
def get_syslog_facility_of_name(facility_name):
    """Wrap the FbSyslogFacilityInfo.facility_id()."""
    return FbSyslogFacilityInfo.facility_id(facility_name)


# =============================================================================
def syslog_facility_id(facility_name):
    """Wrap FbSyslogFacilityInfo.facility_id()."""
    return FbSyslogFacilityInfo.facility_id(facility_name)


# =============================================================================
# vim: fileencoding=utf-8 filetype=python ts=4 et list
