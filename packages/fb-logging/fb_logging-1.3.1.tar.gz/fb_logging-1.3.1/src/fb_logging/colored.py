#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@summary: Additional logging formatter for colored output via console."""

import copy
import logging
import re
from collections.abc import Sequence
from numbers import Number

__version__ = "0.6.2"


# =============================================================================
class ColorNotFoundError(KeyError):
    """Class for an exception in case that a color was not found."""

    # -------------------------------------------------------------------------
    def __init__(self, color):
        """Construct this exception."""
        self.color = color

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        return "Color {!r} not found.".format(self.color)


# =============================================================================
class WrongColorTypeError(TypeError):
    """Class for an exception in case that a wrong type for a color was given."""

    # -------------------------------------------------------------------------
    def __init__(self, color):
        """Construct this exception."""
        self.color = color

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        return "Color {c!r} has wrong type {t}.".format(
            c=self.color, t=self.color.__class__.__name__
        )


# =============================================================================
class Colors:
    """A class for handling terminal color codes."""

    ENDC = 0
    RESET = 0
    BOLD = 1
    GREY40 = 2
    UNDERLINE = 4
    BLINK = 5
    INVERT = 7
    CONCEALD = 8
    STRIKE = 9
    BLACK = 30
    DARK_RED = 31
    DARK_GREEN = 32
    DARK_YELLOW = 33
    DARK_BLUE = 34
    DARK_MAGENTA = 35
    DARK_CYAN = 36
    DARK_WHITE = 37
    BLACK_BG = 40
    RED_BG = 41
    GREEN_BG = 42
    YELLOW_BG = 43
    BLUE_BG = 44
    MAGENTA_BG = 45
    CYAN_BG = 46
    WHITE_BG = 47
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97
    BRIGHT_BLACK_BG = 100
    BRIGHT_RED_BG = 101
    BRIGHT_GREEN_BG = 102
    BRIGHT_YELLOW_BG = 103
    BRIGHT_BLUE_BG = 104
    BRIGHT_MAGENTA_BG = 105
    BRIGHT_CYAN_BG = 106
    BRIGHT_WHITE_BG = 107

    legacy_colors = {
        "GREY30": "BRIGHT_BLACK",
        "GREY65": "DARK_WHITE",
        "GREY70": "BRIGHT_WHITE",
        "GREY20_BG": "BLACK_BG",
        "GREY33_BG": "BRIGHT_BLACK_BG",
        "GREY80_BG": "WHITE_BG",
        "RED": "BRIGHT_RED",
        "GREEN": "BRIGHT_GREEN",
        "YELLOW": "BRIGHT_YELLOW",
        "BLUE": "BRIGHT_BLUE",
        "MAGENTA": "BRIGHT_MAGENTA",
        "CYAN": "BRIGHT_CYAN",
        "WHITE": "BRIGHT_WHITE",
        "LIGHT_BLACK": "BRIGHT_BLACK",
        "LIGHT_RED": "BRIGHT_RED",
        "LIGHT_GREEN": "BRIGHT_GREEN",
        "LIGHT_YELLOW": "BRIGHT_YELLOW",
        "LIGHT_BLUE": "BRIGHT_BLUE",
        "LIGHT_MAGENTA": "BRIGHT_MAGENTA",
        "LIGHT_CYAN": "BRIGHT_CYAN",
        "LIGHT_WHITE": "BRIGHT_WHITE",
        "LIGHT_BLACK_BG": "BRIGHT_BLACK_BG",
        "LIGHT_RED_BG": "BRIGHT_RED_BG",
        "LIGHT_GREEN_BG": "BRIGHT_GREEN_BG",
        "LIGHT_YELLOW_BG": "BRIGHT_YELLOW_BG",
        "LIGHT_BLUE_BG": "BRIGHT_BLUE_BG",
        "LIGHT_MAGENTA_BG": "BRIGHT_MAGENTA_BG",
        "LIGHT_CYAN_BG": "BRIGHT_CYAN_BG",
        "LIGHT_WHITE_BG": "BRIGHT_WHITE_BG",
        "AQUA": "BRIGHT_CYAN",
        "AUQA": "BRIGHT_CYAN",
        "LIGHT_AQUA": "BRIGHT_CYAN",
        "LIGHT_AUQA": "BRIGHT_CYAN",
        "BRIGHT_AQUA": "BRIGHT_CYAN",
        "BRIGHT_AUQA": "BRIGHT_CYAN",
        "DARK_AQUA": "DARK_CYAN",
        "DARK_AUQA": "DARK_CYAN",
        "AQUA_BG": "CYAN_BG",
        "AUQA_BG": "CYAN_BG",
        "LIGHT_AQUA_BG": "BRIGHT_CYAN_BG",
        "LIGHT_AUQA_BG": "BRIGHT_CYAN_BG",
        "BRIGHT_AQUA_BG": "BRIGHT_CYAN_BG",
        "BRIGHT_AUQA_BG": "BRIGHT_CYAN_BG",
        "PURPLE": "BRIGHT_MAGENTA",
        "LIGHT_PURPLE": "BRIGHT_MAGENTA",
        "BRIGHT_PURPLE": "BRIGHT_MAGENTA",
        "DARK_PURPLE": "DARK_MAGENTA",
        "PURPLE_BG": "MAGENTA_BG",
        "LIGHT_PURPLE_BG": "BRIGHT_MAGENTA_BG",
        "BRIGHT_PURPLE_BG": "BRIGHT_MAGENTA_BG",
    }

    # -------------------------------------------------------------------------
    @classmethod
    def termcode_4bit(cls, value):
        """Try to get the numeric value of given 4 Bit color value or font effect name.

        @param color: The color to use, must be a valid 4 Bit color code.
        @type color: str or int

        @raises: ColorNotFoundError if the color was not found.

        @return: The numeric terminal code of the color.
        @rtype: int
        """
        if isinstance(value, bool):
            raise WrongColorTypeError(value)

        if isinstance(value, int):
            return value

        if not isinstance(value, (str, bytes)):
            raise WrongColorTypeError(value)

        key = str(value).upper()
        if key in cls.legacy_colors:
            key = cls.legacy_colors[key]
        if not hasattr(cls, key):
            raise ColorNotFoundError(value)
        return getattr(cls, key)

    # -------------------------------------------------------------------------
    @classmethod
    def termout_8bit_fg(cls, color):
        """Return the terminal code of given 8-bit foreground color."""
        if isinstance(color, Number):
            if isinstance(color, bool):
                raise WrongColorTypeError(color)
            v_int = int(color)
            if v_int != color:
                raise ColorNotFoundError(color)
            if v_int < 0 or v_int > 255:
                raise ColorNotFoundError(color)
            return "\x1b[38;5;{}m".format(v_int)

        raise WrongColorTypeError(color)

    # -------------------------------------------------------------------------
    @classmethod
    def termout_8bit_bg(cls, color):
        """Return the terminal code of given 8-bit background color."""
        if isinstance(color, Number):
            if isinstance(color, bool):
                raise WrongColorTypeError(color)
            v_int = int(color)
            if v_int != color:
                raise ColorNotFoundError(color)
            if v_int < 0 or v_int > 255:
                raise ColorNotFoundError(color)
            return "\x1b[48;5;{}m".format(v_int)

        raise WrongColorTypeError(color)

    # -------------------------------------------------------------------------
    @classmethod
    def colorize_8bit(cls, message, color_fg=None, color_bg=None, font_effect=None):
        """Colorize the given message with a 8-bit color."""
        start_out = ""
        if color_fg is not None:
            start_out += cls.termout_8bit_fg(color_fg)
        if color_bg is not None:
            start_out += cls.termout_8bit_bg(color_bg)
        if font_effect is not None:
            start_out += cls.termcode_4bit(font_effect)

        return start_out + message + cls.termout("reset")

    # -------------------------------------------------------------------------
    @classmethod
    def termout_fg(cls, color):
        """Return the terminal code of given foreground color."""
        if isinstance(color, (list, tuple)):

            if len(color) != 3:
                raise WrongColorTypeError(color)

            for val in color:

                if not isinstance(val, Number):
                    raise WrongColorTypeError(color)

                if isinstance(val, bool):
                    raise WrongColorTypeError(color)

                v_int = int(val)
                if v_int != val:
                    raise WrongColorTypeError(color)
                if v_int < 0 or v_int > 255:
                    raise ColorNotFoundError(color)

            return "\x1b[38;2;{};{};{}m".format(color[0], color[1], color[2])

        raise WrongColorTypeError(color)

    # -------------------------------------------------------------------------
    @classmethod
    def termout_bg(cls, color):
        """Return the terminal code of given background color."""
        if isinstance(color, (list, tuple)):

            if len(color) != 3:
                raise WrongColorTypeError(color)

            for val in color:

                if not isinstance(val, Number):
                    raise WrongColorTypeError(color)

                if isinstance(val, bool):
                    raise WrongColorTypeError(color)

                v_int = int(val)
                if v_int != val:
                    raise WrongColorTypeError(color)
                if v_int < 0 or v_int > 255:
                    raise ColorNotFoundError(color)

            return "\x1b[48;2;{};{};{}m".format(color[0], color[1], color[2])

        raise WrongColorTypeError(color)

    # -------------------------------------------------------------------------
    @classmethod
    def colorize_24bit(cls, message, color_fg=None, color_bg=None):
        """Colorize the given message with a 24-bit color."""
        start_out = ""
        if color_fg is not None:
            start_out += cls.termout_fg(color_fg)
        if color_bg is not None:
            start_out += cls.termout_bg(color_bg)

        return start_out + message + cls.termout("reset")

    # -------------------------------------------------------------------------
    @classmethod
    def termout(cls, color):
        """Output of an ANSII terminal code.

        @param color: The color to use, must be a valid color code.
        @type color: str or int

        @return: The terminal output to start colorized message.
        @rtype: str
        """
        if isinstance(color, (str, bytes)):
            num = cls.termcode_4bit(color)
            return "\x1b[{}m".format(num)

        if isinstance(color, Number):
            return cls.termout_8bit_fg(color)

        if isinstance(color, (list, tuple)):
            return cls.termout_fg(color)

        raise WrongColorTypeError(color)

    # -------------------------------------------------------------------------
    @classmethod
    def colorize(cls, message, color):
        """Colorize the given message message.

        @param message: The message to colorize
        @type message: str
        @param color: The color to use, must be one or a sequence of color codes.
        @type color: str

        @return: the colorized message
        @rtype: str
        """
        start_out = ""
        if isinstance(color, Sequence) and not isinstance(color, (str, bytes)):
            for single_color in color:
                start_out += cls.termout(single_color)
        else:
            start_out = cls.termout(color)

        return start_out + message + cls.termout("reset")

    # -------------------------------------------------------------------------
    @classmethod
    def keys(cls):
        """Return all colornames of this class."""
        ret = []
        re_capital = re.compile(r"^[A-Z][A-Z_0-9]*$")
        for key in sorted(cls.__dict__.keys()):
            if re_capital.match(key):
                ret.append(key)
        return ret


# =============================================================================
def colorstr(message, color):
    """Wrap Color.colorize().

    @param message: The message to colorize
    @type message: str
    @param color: The color to use, must be one or a sequence of color codes.
    @type color: str

    @return: the colorized message
    @rtype: str
    """
    return Colors.colorize(message, color)


# =============================================================================
def colorstr_8bit(message, color_fg=None, color_bg=None, font_effect=None):
    """Wrap Color.colorize_8bit().

    @return: the colorized message
    @rtype: str
    """
    return Colors.colorize_8bit(
        message, color_fg=color_fg, color_bg=color_bg, font_effect=font_effect
    )


# =============================================================================
def colorstr_24bit(message, color_fg=None, color_bg=None):
    """Wrap Color.colorize_24bit().

    @return: the colorized message
    @rtype: str
    """
    return Colors.colorize_24bit(message, color_fg=color_fg, color_bg=color_bg)


# =============================================================================
class ColoredFormatter(logging.Formatter):
    """Format logging messages colorful for screen output.

    A variant of code found at:
    http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored
    """

    level_color_bright = {
        "TRACE": None,
        "DEBUG": "blue",
        "INFO": "cyan",
        "NOTICE": "green",
        "WARNING": "yellow",
        "ERROR": ("bold", "bright_red"),
        "CRITICAL": ("bold", "yellow", "red_bg"),
    }

    level_color_dark = {
        "TRACE": None,
        "DEBUG": "dark_blue",
        "INFO": "dark_cyan",
        "NOTICE": "dark_green",
        "WARNING": "dark_yellow",
        "ERROR": "dark_red",
        "CRITICAL": ("bold", "yellow", "red_bg"),
    }

    # -------------------------------------------------------------------------
    def __init__(self, fmt=None, datefmt=None, dark=False, colorize_msg=False):
        """Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default. Allow for specialized date formatting with the optional
        datefmt argument (if omitted, you get the ISO8601 format).
        """
        logging.Formatter.__init__(self, fmt, datefmt)

        self.level_color = {}

        if dark:
            # changing the default colors to "dark" because the xterm plugin
            # for Jenkins cannot use bright colors
            # see: http://stackoverflow.com/a/28071761
            self.level_color = copy.copy(self.level_color_dark)
        else:
            self.level_color = copy.copy(self.level_color_bright)

        self._colorize_msg = False
        self.colorize_msg = colorize_msg

    # -----------------------------------------------------------
    @property
    def colorize_msg(self):
        """Return whether the logging message should also be colorized."""
        return getattr(self, "_colorize_msg", False)

    @colorize_msg.setter
    def colorize_msg(self, value):
        self._colorize_msg = bool(value)

    # -----------------------------------------------------------
    @property
    def color_debug(self):
        """Return the color used to output debug messages."""
        return self.level_color["DEBUG"]

    @color_debug.setter
    def color_debug(self, value):
        self.level_color["DEBUG"] = value

    # -----------------------------------------------------------
    @property
    def color_info(self):
        """Return the color used to output info messages."""
        return self.level_color["INFO"]

    @color_info.setter
    def color_info(self, value):
        self.level_color["INFO"] = value

    # -----------------------------------------------------------
    @property
    def color_warning(self):
        """Return the color used to output warning messages."""
        return self.level_color["WARNING"]

    @color_warning.setter
    def color_warning(self, value):
        self.level_color["WARNING"] = value

    # -----------------------------------------------------------
    @property
    def color_error(self):
        """Return the color used to output error messages."""
        return self.level_color["ERROR"]

    @color_error.setter
    def color_error(self, value):
        self.level_color["ERROR"] = value

    # -----------------------------------------------------------
    @property
    def color_critical(self):
        """Return the color used to output critical messages."""
        return self.level_color["CRITICAL"]

    @color_critical.setter
    def color_critical(self, value):
        self.level_color["CRITICAL"] = value

    # -------------------------------------------------------------------------
    def format(self, record):  # noqa A003.
        """Format the specified record as text."""
        rcrd = copy.copy(record)
        levelname = rcrd.levelname

        if levelname in self.level_color:

            rcrd.name = colorstr(rcrd.name, "bold")
            rcrd.filename = colorstr(rcrd.filename, "bold")
            rcrd.module = colorstr(rcrd.module, "bold")
            rcrd.funcName = colorstr(rcrd.funcName, "bold")
            rcrd.pathname = colorstr(rcrd.pathname, "bold")
            rcrd.processName = colorstr(rcrd.processName, "bold")
            rcrd.threadName = colorstr(rcrd.threadName, "bold")

            clr = self.level_color[levelname]
            if clr is not None:
                rcrd.levelname = colorstr(levelname, clr)
                if self.colorize_msg:
                    rcrd.msg = colorstr(rcrd.msg, clr)

        return logging.Formatter.format(self, rcrd)


# =============================================================================
# vim: fileencoding=utf-8 filetype=python ts=4 et list
