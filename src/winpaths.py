# winpaths.py

"""Functions for getting system/language/user dependent paths on windows.

All path names returned by the functions of this module are unicode strings.
"""

__all__ = [
    "HKCU",
    "HKLM",
    "SHELL_FOLDERS",
    "USER_SHELL_FOLDERS",
    "expandvars",
    "get_appdata",
    "get_common_shellfolders",
    "get_homedir",
    "get_sharedconf",
    "get_shellfolders",
    "get_userconf",
    "get_windir",
]


__module__ = "winpaths"
__author__ = "Christopher Arndt"
__version__ = "0.2"
__revision__ = "$Rev$"
__date__ = "$Date$"
__copyright__ = "Python license"

# Modified 2020/05/01 to remove Python 2 compatibility code.
# Modified 2021/04/10 to reformat and add type safety.
# Modified 2022/03/29 to ignore type linting problems on Linux.


import os

try:
    import winreg
except ImportError:
    # Well, whoops. Presumably we're not running Windows. Pass silently.
    pass

else:
    SHELL_FOLDERS = (
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    )

    USER_SHELL_FOLDERS = (
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    )

    HKCU = winreg.HKEY_CURRENT_USER  # type: ignore
    HKLM = winreg.HKEY_LOCAL_MACHINE  # type: ignore

    # helper functions

    def _substenv(m):
        return os.environ.get(m.group(1), m.group(0))

    _env_rx = None

    def expandvars(s):
        """Expand environment variables of form %var%.

        Unknown variables are left unchanged.
        """

        global _env_rx

        if "%" not in s:
            return s

        if _env_rx is None:
            import re

            _env_rx = re.compile(r"%([^|<>=^%]+)%")

        return _env_rx.sub(_substenv, s)

    def _get_reg_value(key, subkey, name):
        """Return registry value specified by key, subkey, and name.

        Environment variables in values of type REG_EXPAND_SZ are expanded
        if possible.
        """

        key = winreg.OpenKey(key, subkey)  # type: ignore

        try:
            ret = winreg.QueryValueEx(key, name)  # type: ignore

        except WindowsError:  # type: ignore  # actually valid on Windows.
            return ""

        else:
            key.Close()

            if ret[1] == winreg.REG_EXPAND_SZ:  # type: ignore
                return expandvars(ret[0])

            else:
                return ret[0]

    def _get_reg_user_value(key, name):
        """Return a windows registry value from the CURRENT_USER branch."""

        return _get_reg_value(HKCU, key, name)

    def _get_reg_machine_value(key, name):
        """Return a windows registry value from the LOCAL_MACHINE branch."""

        return _get_reg_value(HKLM, key, name)

    # public functions

    def get_appdata():
        "Return path of directory where apps should store user specific data."

        return _get_reg_user_value(SHELL_FOLDERS, "AppData")

    def get_common_shellfolders():
        """Return mapping of shell folder names (all users) to paths."""

        return get_shellfolders(branch=HKLM)

    def get_homedir():
        """Return path to user home directory, i.e. 'My Files'."""

        return _get_reg_user_value(SHELL_FOLDERS, "Personal")

    def get_sharedconf(vendor, prog, *args):
        """Return path to shared configuration data for 'prog' from 'vendor'.

        Additional arguments are appended via os.path.join().

        See also: get_user_conf()
        """

        return os.path.join(
            _get_reg_machine_value(SHELL_FOLDERS, "Common AppData"),
            vendor,
            prog,
            *args,
        )

    def get_shellfolders(branch=HKCU, key=SHELL_FOLDERS):
        """Return mapping of shell folder names (current user) to paths."""

        key = winreg.OpenKey(branch, key)  # type: ignore
        folders = {}
        i = 0

        while True:
            try:
                ret = winreg.EnumValue(key, i)  # type: ignore

                if ret[2] == winreg.REG_EXPAND_SZ:  # type: ignore
                    folders[ret[0]] = expandvars(ret[1])

                else:
                    folders[ret[0]] = ret[1]

            except WindowsError:  # type: ignore  # actually valid on Windows.
                break

            i += 1

        key.Close()

        return folders

    def get_userconf(vendor, prog, *args):
        """Return path to user configuration data for 'prog' from 'vendor'.

        Additional arguments are appended via os.path.join(), e.g.
        use like this:

        optionsfn = get_userconf( "ACME Soft", "Exploder", "Options.xml" )
        """

        return os.path.join(get_appdata(), vendor, prog, *args)

    def get_windir():
        "Convenience function to get path to windows installation directory."

        return str(os.environ["WINDIR"])
