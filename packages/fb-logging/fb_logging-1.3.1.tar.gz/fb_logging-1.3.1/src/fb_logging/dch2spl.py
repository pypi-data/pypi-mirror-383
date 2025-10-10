#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: A script for converting a Debian changelog into log entries of a RPM spec file.

@author: Frank Brehm
@contact: frank@brehm.online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import print_function

# Standard modules
import datetime
import logging
import os
import platform
import pprint
import re
import sys
import textwrap
import warnings
from pathlib import Path

# 3rd party modules
import click

# Own modules
from fb_logging import __version__ as __pkg_version__
from fb_logging.colored import ColoredFormatter
from fb_logging.deb_changelog import Changelog

# from fb_logging.deb_changelog import Changelog

__version__ = "0.2.0"

LOG = logging.getLogger(__name__)


# =============================================================================
def pp(value, indent=4, width=150, depth=None):
    """
    Return a pretty print string of the given value.

    @return: pretty print string
    @rtype: str
    """
    pretty_printer = pprint.PrettyPrinter(indent=indent, width=width, depth=depth)
    return pretty_printer.pformat(value)


# =============================================================================
class Dch2SpecLogEnv(object):
    """
    Click context environment class for the dch2speclog application.

    Converts a Debian changelog into log entries of a RPM spec file.
    """

    re_emptyline = re.compile(r"^\s*$")
    re_start_line = re.compile(r"^  \* (.*)")
    re_next_line = re.compile(r"^    (.*)")
    re_day_str = re.compile(r"\s+\d\d:\d\d:\d\d\s+[+-]?\d{4}$")

    output_line_width = 70

    # -------------------------------------------------------------------------
    @classmethod
    def get_generic_appname(cls, appname=None):
        """Get the base name of the currently running application."""
        if appname:
            v = str(appname).strip()
            if v:
                return v
        return os.path.basename(sys.argv[0])

    # -------------------------------------------------------------------------
    @classmethod
    def terminal_can_colors(cls, debug=False):
        """
        Detect, whether the current terminal is able to perform ANSI color sequences.

        Both stdout and stderr file handles are inspected.

        @return: both stdout and stderr can perform ANSI color sequences
        @rtype: bool
        """
        cur_term = ""
        if "TERM" in os.environ:
            cur_term = os.environ["TERM"].lower().strip()

        colored_term_list = (
            r"ansi",
            r"linux.*",
            r"screen.*",
            r"[xeak]term.*",
            r"gnome.*",
            r"rxvt.*",
            r"interix",
        )
        term_pattern = r"^(?:" + r"|".join(colored_term_list) + r")$"
        re_term = re.compile(term_pattern)

        ansi_term = False
        env_term_has_colors = False

        if cur_term:
            if cur_term == "ansi":
                env_term_has_colors = True
                ansi_term = True
            elif re_term.search(cur_term):
                env_term_has_colors = True
        if debug:
            sys.stderr.write(
                "ansi_term: {a!r}, env_term_has_colors: {h!r}\n".format(
                    a=ansi_term, h=env_term_has_colors
                )
            )

        has_colors = False
        if env_term_has_colors:
            has_colors = True
        for handle in [sys.stdout, sys.stderr]:
            if hasattr(handle, "isatty") and handle.isatty():
                if debug:
                    msg = "{} is a tty.".format(handle.name)
                    sys.stderr.write(msg + "\n")
                if platform.system() == "Windows" and not ansi_term:
                    if debug:
                        sys.stderr.write("Platform is Windows and not ansi_term.\n")
                    has_colors = False
            else:
                if debug:
                    msg = "{} is not a tty.".format(handle.name)
                    sys.stderr.write(msg + "\n")
                if ansi_term:
                    pass
                else:
                    has_colors = False

        return has_colors

    # -------------------------------------------------------------------------
    def __init__(
        self, changelog_file, appname=None, verbose=0, version=__pkg_version__, has_colors=None
    ):
        """Initialise the application object."""
        if changelog_file is None:
            self.changelog_file = None
        else:
            self.changelog_file = Path(changelog_file)
        if appname:
            self.appname = self.get_generic_appname()
        else:
            self.appname = self.get_generic_appname()
        self.verbose = verbose
        self.version = version
        if has_colors is not None:
            self.has_colors = bool(has_colors)
        else:
            self.has_colors = self.terminal_can_color()

        self.init_logging()

        if self.verbose > 1:
            LOG.debug(f"Parameter 'has_colors' was {has_colors!r}.")

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""
        out = "<%s(" % (self.__class__.__name__)

        fields = []
        cfile = None
        if self.changelog_file is not None:
            cfile = str(self.changelog_file)

        fields.append(f"changelog_file={cfile!r}")
        fields.append(f"appname={self.appname!r}")
        fields.append(f"verbose={self.verbose!r}")
        fields.append(f"version={self.version!r}")
        fields.append(f"has_colors={self.has_colors!r}")

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def terminal_can_color(self):
        """
        Detect, whether the current terminal is able to perform ANSI color sequences.

        Both stdout and stderr file handles are inspected.

        @return: both stdout and stderr can perform ANSI color sequences
        @rtype: bool

        """
        if self.verbose > 3:
            return self.terminal_can_colors(debug=True)
        return self.terminal_can_colors(debug=False)

    # -------------------------------------------------------------------------
    def init_logging(self):
        """
        Initialize the logger object.

        It creates a colored loghandler with all output to STDERR.
        Maybe overridden in descendant classes.

        @return: None
        """
        log_level = logging.INFO
        if self.verbose:
            log_level = logging.DEBUG

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # create formatter
        format_str = ""
        if self.verbose:
            format_str = "[%(asctime)s]: "
        format_str += self.appname + ": "
        if self.verbose:
            if self.verbose > 1:
                format_str += "%(name)s(%(lineno)d) %(funcName)s() "
            else:
                format_str += "%(name)s "
        format_str += "%(levelname)s - %(message)s"
        formatter = None
        if self.has_colors:
            formatter = ColoredFormatter(format_str)
        else:
            formatter = logging.Formatter(format_str)

        # create log handler for console output
        lh_console = logging.StreamHandler(sys.stderr)
        lh_console.setLevel(log_level)
        lh_console.setFormatter(formatter)

        root_logger.addHandler(lh_console)

        return

    # -------------------------------------------------------------------------
    def __call__(self):
        """
        Execute the main action of converting.

        Makes the application object callable.
        """
        if self.changelog_file:
            cfile = str(self.changelog_file)
            LOG.debug(f"Reading {cfile!r} ...")
            with self.changelog_file.open("r", encoding="utf-8", errors="backslashreplace") as fh:
                self.convert(fh, str(self.changelog_file))
        else:
            self.convert(sys.stdin, "STDIN")

    # -------------------------------------------------------------------------
    def mangle_changes(self, changes):
        """Transform the changes into the RPM chngelog format."""
        clist = []
        change = None

        for line in changes:

            if self.re_emptyline.match(line):
                continue

            m = self.re_start_line.match(line)
            if m:
                if change:
                    clist.append(change)
                change = m.group(1)
                continue

            m = self.re_next_line.match(line)
            if m:
                if change:
                    change += " " + m.group(1)
                else:
                    change = m.group(1)
                continue

            warnings.warn(
                "Could not evaluate Changelog entry {!r}.".format(line),
                SyntaxWarning,
                stacklevel=1,
            )

        if change:
            clist.append(change)

        return clist

    # -------------------------------------------------------------------------
    def convert(self, fh, filename):
        """Transform the complete contenet of the given changelog file into RPM changelog files."""
        ch = None

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ch = Changelog(fh)

            if len(w):
                msg = "There were {nr} warnings on reading {f!r}.".format(nr=len(w), f=filename)
                LOG.warning(msg)
                for msg in w:
                    category = msg.category.__name__
                    s = f"{category}: {msg.message}\n"
                    LOG.warning(s)
                sys.exit(5)

        LOG.debug("Changelog {f!r} has {nr} entries.".format(f=filename, nr=len(ch)))

        days = {}

        for block in ch:

            lines = []
            day_str = self.re_day_str.sub("", block.date)
            date = datetime.datetime.strptime(day_str, "%a, %d %b %Y")

            day = date.strftime("%Y-%m-%d")
            author = block.author
            version = str(block.version)
            if not block.version.debian_revision:
                version += "-1"
            lines.append(
                "*   {date} {author} {version}".format(date=date, author=author, version=version)
            )

            changes = self.mangle_changes(block._changes)

            if day not in days:
                days[day] = {
                    "date": date.strftime("%a %b %d %Y"),
                    "author": author,
                    "version": version,
                    "changes": changes,
                }
            else:
                for change in changes:
                    days[day]["changes"].append(change)

        for day in sorted(days.keys(), reverse=True):
            lines = []
            block = days[day]
            lines.append(
                "*   {date} {author} {version}".format(
                    date=block["date"], author=block["author"], version=block["version"]
                )
            )

            for change in block["changes"]:
                for line in textwrap.wrap(
                    change, width=self.output_line_width, initial_indent="-   ",
                    subsequent_indent="    "
                ):
                    lines.append(line)

            click.echo("\n".join(lines))


# =============================================================================

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "changelog_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, path_type=Path),
    required=False,
)
@click.option(
    "--color/--no-color", "has_color", default=None, help="Set colored output for messages."
)
@click.option(
    "-v", "--verbose", count=True, type=click.IntRange(0, 5), help="Increase the verbosity level."
)
@click.version_option()
@click.pass_context
def main(ctx, changelog_file, has_color, verbose):
    """
    Convert a Debian CHANGELOG_FILE into log entries of a RPM spec file.

    If CHANGELOG_FILE is omitted, then the input will be read from STDIN.
    """
    ctx.obj = Dch2SpecLogEnv(changelog_file, verbose=verbose, has_colors=has_color)

    if verbose > 2:
        click.echo(
            "{c}-Object:\n{a}".format(c=ctx.__class__.__name__, a=pp(ctx.__dict__)),
            file=sys.stderr,
        )

    ctx.obj()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
