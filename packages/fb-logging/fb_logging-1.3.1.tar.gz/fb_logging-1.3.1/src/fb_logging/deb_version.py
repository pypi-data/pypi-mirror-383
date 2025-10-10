"""Facilities to deal with Debian-specific metadata."""

# Copyright (C) 2005 Florian Weimer <fw@deneb.enyo.de>
# Copyright (C) 2010 John Wright <jsw@debian.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from __future__ import absolute_import, print_function

import re
import warnings

try:
    # pylint: disable=unused-import
    from typing import (  # noqa: F401
        Any,
        Optional,
        Text,
        Union,
    )
except ImportError:
    # Lack of typing is not important at runtime
    pass


# =============================================================================
def function_deprecated_by(func):
    """Return a function that warns it is deprecated by another function.

    Returns a new function that warns it is deprecated by function
    ``func``, then acts as a pass-through wrapper for ``func``.
    """
    try:
        func_name = func.__name__
    except AttributeError:
        func_name = func.__func__.__name__
    warn_msg = "Use %s instead" % func_name

    def deprecated_func(*args, **kwargs):
        warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return deprecated_func


# =============================================================================
class BaseVersion(object):
    """Base class for classes representing Debian versions.

    It doesn't implement any comparison, but it does check for valid versions
    according to Section 5.6.12 in the Debian Policy Manual.  Since splitting
    the version into epoch, upstream_version, and debian_revision components is
    pretty much free with the validation, it sets those fields as properties of
    the object, and sets the raw version to the full_version property.  A
    missing epoch or debian_revision results in the respective property set to
    None.  Setting any of the properties results in the full_version being
    recomputed and the rest of the properties set from that.

    It also implements __str__, just returning the raw version given to the
    initializer.
    """

    re_valid_version = re.compile(
        r"^((?P<epoch>\d+):)?"
        "(?P<upstream_version>[A-Za-z0-9.+:~-]+?)"
        "(-(?P<debian_revision>[A-Za-z0-9+.~]+))?$"
    )
    magic_attrs = (
        "full_version",
        "epoch",
        "upstream_version",
        "debian_revision",
        "debian_version",
    )

    # -------------------------------------------------------------------------
    def __init__(self, version):
        """Construct this object."""
        # type: (Union[str, BaseVersion]) -> None
        if isinstance(version, BaseVersion):
            version = str(version)
        self.full_version = version

    # -------------------------------------------------------------------------
    def _set_full_version(self, version):
        # type: (str) -> None
        m = self.re_valid_version.match(version)
        if not m:
            raise ValueError("Invalid version string %r" % version)
        # If there no epoch ("1:..."), then the upstream version can not
        # contain a :.
        if m.group("epoch") is None and ":" in m.group("upstream_version"):
            raise ValueError("Invalid version string %r" % version)

        # pylint: disable=attribute-defined-outside-init
        self.__full_version = version
        self.__epoch = m.group("epoch")
        self.__upstream_version = m.group("upstream_version")
        self.__debian_revision = m.group("debian_revision")

    # -------------------------------------------------------------------------
    def __setattr__(self, attr, value):
        """Override attribute setter."""
        # type: (str, Optional[Text]) -> None
        if attr not in self.magic_attrs:
            super(BaseVersion, self).__setattr__(attr, value)
            return

        # For compatibility with the old changelog.Version class
        if attr == "debian_version":
            attr = "debian_revision"

        if attr == "full_version":
            self._set_full_version(str(value))
        else:
            if value is not None:
                value = str(value)
            private = "_BaseVersion__%s" % attr
            old_value = getattr(self, private)
            setattr(self, private, value)
            try:
                self._update_full_version()
            except ValueError:
                # Don't leave it in an invalid state
                setattr(self, private, old_value)
                self._update_full_version()
                raise ValueError("Setting %s to %r results in invalid version" % (attr, value))

    # -------------------------------------------------------------------------
    def __getattr__(self, attr):
        """Override attribute getter."""
        # type: (str) -> Optional[str]
        if attr not in self.magic_attrs:
            return super(BaseVersion, self).__getattribute__(attr)

        # For compatibility with the old changelog.Version class
        if attr == "debian_version":
            attr = "debian_revision"

        private = "_BaseVersion__%s" % attr
        return getattr(self, private)

    # -------------------------------------------------------------------------
    def _update_full_version(self):
        # type: () -> None
        version = ""
        if self.__epoch is not None:
            version += self.__epoch + ":"
        version += self.__upstream_version
        if self.__debian_revision:
            version += "-" + self.__debian_revision
        self.full_version = version

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into str."""
        # type: () -> str
        return self.full_version

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Typecast into str for reproduction."""
        # type: () -> str
        return "%s('%s')" % (self.__class__.__name__, self)

    # -------------------------------------------------------------------------
    def _compare(self, other):
        raise NotImplementedError

    # TODO: Once we support only Python >= 2.7, we can simplify this using
    # @functools.total_ordering.

    # -------------------------------------------------------------------------
    def __lt__(self, other):
        """Operator '<'."""
        # type: (Any) -> bool
        return self._compare(other) < 0

    # -------------------------------------------------------------------------
    def __le__(self, other):
        """Operator '<='."""
        # type: (Any) -> bool
        return self._compare(other) <= 0

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Operator '=='."""
        # type: (Any) -> bool
        return self._compare(other) == 0

    # -------------------------------------------------------------------------
    def __ne__(self, other):
        """Operator '!='."""
        # type: (Any) -> bool
        return self._compare(other) != 0

    # -------------------------------------------------------------------------
    def __ge__(self, other):
        """Operator '>'."""
        # type: (Any) -> bool
        return self._compare(other) >= 0

    # -------------------------------------------------------------------------
    def __gt__(self, other):
        """Operator '>='."""
        # type: (Any) -> bool
        return self._compare(other) > 0

    # -------------------------------------------------------------------------
    def __hash__(self):
        """Generate a hash value of the initialized object."""
        return hash(str(self))


# =============================================================================
# NativeVersion based on the DpkgVersion class by Raphael Hertzog in
# svn://svn.debian.org/qa/trunk/pts/www/bin/common.py r2361
class Version(BaseVersion):
    """Represents a Debian package version, with native Python comparison."""

    re_all_digits_or_not = re.compile(r"\d+|\D+")
    re_digits = re.compile(r"\d+")
    re_digit = re.compile(r"\d")
    re_alpha = re.compile("[A-Za-z]")

    # -------------------------------------------------------------------------
    def _compare(self, other):
        # type: (Any) -> int
        # Convert other into an instance of BaseVersion if it's not already.
        # (All we need is epoch, upstream_version, and debian_revision
        # attributes, which BaseVersion gives us.) Requires other's string
        # representation to be the raw version.

        # If other is not defined, then the current version is bigger
        if other is None:
            return 1

        if not isinstance(other, BaseVersion):
            try:
                other = BaseVersion(str(other))
            except ValueError as e:
                raise ValueError("Couldn't convert %r to BaseVersion: %s" % (other, e))

        lepoch = int(self.epoch or "0")
        repoch = int(other.epoch or "0")
        if lepoch < repoch:
            return -1
        if lepoch > repoch:
            return 1
        res = self._version_cmp_part(self.upstream_version or "0", other.upstream_version or "0")
        if res != 0:
            return res
        return self._version_cmp_part(self.debian_revision or "0", other.debian_revision or "0")

    # -------------------------------------------------------------------------
    @classmethod
    def _order(cls, x):
        # type: (str) -> int
        """Return an integer value for character x."""
        if x == "~":
            return -1
        if cls.re_digit.match(x):
            return int(x) + 1
        if cls.re_alpha.match(x):
            return ord(x)
        return ord(x) + 256

    # -------------------------------------------------------------------------
    @classmethod
    def _version_cmp_string(cls, va, vb):
        # type: (str, str) -> int
        la = [cls._order(x) for x in va]
        lb = [cls._order(x) for x in vb]
        while la or lb:
            a = 0
            b = 0
            if la:
                a = la.pop(0)
            if lb:
                b = lb.pop(0)
            if a < b:
                return -1
            if a > b:
                return 1
        return 0

    # -------------------------------------------------------------------------
    @classmethod
    def _version_cmp_part(cls, va, vb):
        # type: (str, str) -> int
        la = cls.re_all_digits_or_not.findall(va)
        lb = cls.re_all_digits_or_not.findall(vb)
        while la or lb:
            a = "0"
            b = "0"
            if la:
                a = la.pop(0)
            if lb:
                b = lb.pop(0)
            if cls.re_digits.match(a) and cls.re_digits.match(b):
                aval = int(a)
                bval = int(b)
                if aval < bval:
                    return -1
                if aval > bval:
                    return 1
            else:
                res = cls._version_cmp_string(a, b)
                if res != 0:
                    return res
        return 0


# =============================================================================
def version_compare(a, b):
    """Compare two version strings."""
    # type: (Any, Any) -> int
    va = Version(a)
    vb = Version(b)
    if va < vb:
        return -1
    if va > vb:
        return 1
    return 0


# =============================================================================
# vim: fileencoding=utf-8 filetype=python ts=4 et list
