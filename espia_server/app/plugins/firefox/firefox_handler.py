import argparse
import ctypes as ct
import locale
import logging
import os
import pathlib
import platform
import shutil
import sys
from base64 import b64decode
from configparser import ConfigParser
from typing import Optional, Iterator, Any

_FIREFOX_PRODUCT = {
    "Passwords": [],
    "Cookies": []
}
LOG: logging.Logger
VERBOSE = False
SYSTEM = platform.system()
SYS64 = sys.maxsize > 2 ** 32
DEFAULT_ENCODING = "utf-8"

PWStore = list[dict[str, str]]


class NotFoundError(Exception):
    """Exception to handle situations where a credentials file is not found
    """
    pass


class Exit(Exception):
    """Exception to allow a clean exit from any point in execution
    """
    CLEAN = 0
    ERROR = 1
    MISSING_PROFILEINI = 2
    MISSING_SECRETS = 3
    BAD_PROFILEINI = 4
    LOCATION_NO_DIRECTORY = 5
    BAD_SECRETS = 6
    BAD_LOCALE = 7

    FAIL_LOCATE_NSS = 10
    FAIL_LOAD_NSS = 11
    FAIL_INIT_NSS = 12
    FAIL_NSS_KEYSLOT = 13
    FAIL_SHUTDOWN_NSS = 14
    BAD_MASTER_PASSWORD = 15
    NEED_MASTER_PASSWORD = 16

    PASSSTORE_NOT_INIT = 20
    PASSSTORE_MISSING = 21
    PASSSTORE_ERROR = 22

    READ_GOT_EOF = 30
    MISSING_CHOICE = 31
    NO_SUCH_PROFILE = 32

    UNKNOWN_ERROR = 100
    KEYBOARD_INTERRUPT = 102

    def __init__(self, exitcode):
        self.exitcode = exitcode

    def __unicode__(self):
        return f"Premature program exit with exit code {self.exitcode}"


class Credentials:
    """Base credentials backend manager
    """

    def __init__(self, db):
        self.db = db

        LOG.debug("Database location: %s", self.db)
        if not os.path.isfile(db):
            raise NotFoundError(f"ERROR - {db} database not found\n")

        LOG.info("Using %s for credentials.", db)

    def __iter__(self) -> Iterator[tuple[str, str, str, int]]:
        pass

    def done(self):
        """Override this method if the credentials subclass needs to do any
        action after interaction
        """
        pass


def find_nss(locations, nssname) -> ct.CDLL:
    """Locate nss is one of the many possible locations
    """
    fail_errors: list[tuple[str, str]] = []

    OS = ("Windows", "Darwin")

    for loc in locations:
        nsslib = os.path.join(loc, nssname)

        if SYSTEM in OS:
            # On windows in order to find DLLs referenced by nss3.dll
            # we need to have those locations on PATH
            os.environ["PATH"] = ';'.join([loc, os.environ["PATH"]])
            # However this doesn't seem to work on all setups and needs to be
            # set before starting python so as a workaround we chdir to
            # Firefox's nss3.dll/libnss3.dylib location
            if loc:
                if not os.path.isdir(loc):
                    # No point in trying to load from paths that don't exist
                    continue

                workdir = os.getcwd()
                os.chdir(loc)

        try:
            nss: ct.CDLL = ct.CDLL(nsslib)
        except OSError as e:
            fail_errors.append((nsslib, str(e)))
        else:
            return nss
        finally:
            if SYSTEM in OS and loc:
                # Restore workdir changed above
                os.chdir(workdir)

    else:
        LOG.error("Couldn't find or load '%s'. This library is essential "
                  "to interact with your Mozilla profile.", nssname)
        LOG.error("If you are seeing this error please perform a system-wide "
                  "search for '%s' and file a bug report indicating any "
                  "location found. Thanks!", nssname)
        LOG.error("Alternatively you can try launching firefox_decrypt "
                  "from the location where you found '%s'. "
                  "That is 'cd' or 'chdir' to that location and run "
                  "firefox_decrypt from there.", nssname)

        LOG.error("Please also include the following on any bug report. "
                  "Errors seen while searching/loading NSS:")

        for target, error in fail_errors:
            LOG.error("Error when loading %s was %s", target, error)

        raise Exit(Exit.FAIL_LOCATE_NSS)


def load_libnss():
    """Load libnss into python using the CDLL interface
    """
    if SYSTEM == "Windows":
        nssname = "nss3.dll"
        if SYS64:
            locations: list[str] = [
                "",  # Current directory or system lib finder
                os.path.expanduser("~\\AppData\\Local\\Mozilla Firefox"),
                os.path.expanduser("~\\AppData\\Local\\Mozilla Thunderbird"),
                os.path.expanduser("~\\AppData\\Local\\Nightly"),
                os.path.expanduser("~\\AppData\\Local\\SeaMonkey"),
                os.path.expanduser("~\\AppData\\Local\\Waterfox"),
                "C:\\Program Files\\Mozilla Firefox",
                "C:\\Program Files\\Mozilla Thunderbird",
                "C:\\Program Files\\Nightly",
                "C:\\Program Files\\SeaMonkey",
                "C:\\Program Files\\Waterfox",
            ]
        else:
            locations: list[str] = [
                "",  # Current directory or system lib finder
                "C:\\Program Files (x86)\\Mozilla Firefox",
                "C:\\Program Files (x86)\\Mozilla Thunderbird",
                "C:\\Program Files (x86)\\Nightly",
                "C:\\Program Files (x86)\\SeaMonkey",
                "C:\\Program Files (x86)\\Waterfox",
                # On windows 32bit these folders can also be 32bit
                os.path.expanduser("~\\AppData\\Local\\Mozilla Firefox"),
                os.path.expanduser("~\\AppData\\Local\\Mozilla Thunderbird"),
                os.path.expanduser("~\\AppData\\Local\\Nightly"),
                os.path.expanduser("~\\AppData\\Local\\SeaMonkey"),
                os.path.expanduser("~\\AppData\\Local\\Waterfox"),
                "C:\\Program Files\\Mozilla Firefox",
                "C:\\Program Files\\Mozilla Thunderbird",
                "C:\\Program Files\\Nightly",
                "C:\\Program Files\\SeaMonkey",
                "C:\\Program Files\\Waterfox",
            ]

        # If either of the supported software is in PATH try to use it
        software = ["firefox", "thunderbird", "waterfox", "seamonkey"]
        for binary in software:
            location: Optional[str] = shutil.which(binary)
            if location is not None:
                nsslocation: str = os.path.join(os.path.dirname(location), nssname)
                locations.append(nsslocation)

    elif SYSTEM == "Darwin":
        nssname = "libnss3.dylib"
        locations = (
            "",
            "/usr/local/lib/nss",
            "/usr/local/lib",
            "/opt/local/lib/nss",
            "/sw/lib/firefox",
            "/sw/lib/mozilla",
            "/usr/local/opt/nss/lib",
            "/opt/pkg/lib/nss",
            "/Applications/Firefox.app/Contents/MacOS"
        )

    else:
        nssname = "libnss3.so"
        if SYS64:
            locations = (
                "",  # Current directory or system lib finder
                "/usr/lib64",
                "/usr/lib64/nss",
                "/usr/lib",
                "/usr/lib/nss",
                "/usr/local/lib",
                "/usr/local/lib/nss",
                "/opt/local/lib",
                "/opt/local/lib/nss",
                os.path.expanduser("~/.nix-profile/lib"),
            )
        else:
            locations = (
                "",  # Current directory or system lib finder
                "/usr/lib",
                "/usr/lib/nss",
                "/usr/lib32",
                "/usr/lib32/nss",
                "/usr/lib64",
                "/usr/lib64/nss",
                "/usr/local/lib",
                "/usr/local/lib/nss",
                "/opt/local/lib",
                "/opt/local/lib/nss",
                os.path.expanduser("~/.nix-profile/lib"),
            )

    # If this succeeds libnss was loaded
    return find_nss(locations, nssname)


class c_char_p_fromstr(ct.c_char_p):
    """ctypes char_p override that handles encoding str to bytes"""

    def from_param(self):
        return self.encode(DEFAULT_ENCODING)


class NSSProxy:
    class SECItem(ct.Structure):
        """struct needed to interact with libnss
        """
        _fields_ = [
            ('type', ct.c_uint),
            ('data', ct.c_char_p),  # actually: unsigned char *
            ('len', ct.c_uint),
        ]

        def decode_data(self):
            _bytes = ct.string_at(self.data, self.len)
            return _bytes.decode(DEFAULT_ENCODING)

    class PK11SlotInfo(ct.Structure):
        """Opaque structure representing a logical PKCS slot
        """

    def __init__(self):
        # Locate libnss and try loading it
        self.libnss = load_libnss()

        SlotInfoPtr = ct.POINTER(self.PK11SlotInfo)
        SECItemPtr = ct.POINTER(self.SECItem)

        self._set_ctypes(ct.c_int, "NSS_Init", c_char_p_fromstr)
        self._set_ctypes(ct.c_int, "NSS_Shutdown")
        self._set_ctypes(SlotInfoPtr, "PK11_GetInternalKeySlot")
        self._set_ctypes(None, "PK11_FreeSlot", SlotInfoPtr)
        self._set_ctypes(ct.c_int, "PK11_NeedLogin", SlotInfoPtr)
        self._set_ctypes(ct.c_int, "PK11_CheckUserPassword", SlotInfoPtr, c_char_p_fromstr)
        self._set_ctypes(ct.c_int, "PK11SDR_Decrypt", SECItemPtr, SECItemPtr, ct.c_void_p)
        self._set_ctypes(None, "SECITEM_ZfreeItem", SECItemPtr, ct.c_int)

        # for error handling
        self._set_ctypes(ct.c_int, "PORT_GetError")
        self._set_ctypes(ct.c_char_p, "PR_ErrorToName", ct.c_int)
        self._set_ctypes(ct.c_char_p, "PR_ErrorToString", ct.c_int, ct.c_uint32)

    def _set_ctypes(self, restype, name, *argtypes):
        """Set input/output types on libnss C functions for automatic type casting
        """
        res = getattr(self.libnss, name)
        res.argtypes = argtypes
        res.restype = restype

        # Transparently handle decoding to string when returning a c_char_p
        if restype == ct.c_char_p:
            def _decode(result, func, *args):
                return result.decode(DEFAULT_ENCODING)

            res.errcheck = _decode

        setattr(self, "_" + name, res)

    def initialize(self, profile: pathlib.Path):
        profile_path = f"sql:{profile}"
        LOG.debug("Initializing NSS with profile '%s'", profile_path)
        err_status: int = self._NSS_Init(profile_path)
        LOG.debug("Initializing NSS returned %s", err_status)

        if err_status:
            self.handle_error(
                Exit.FAIL_INIT_NSS,
                "Couldn't initialize NSS, maybe '%s' is not a valid profile?",
                profile,
            )

    def shutdown(self):
        err_status: int = self._NSS_Shutdown()

        if err_status:
            self.handle_error(
                Exit.FAIL_SHUTDOWN_NSS,
                "Couldn't shutdown current NSS profile",
            )

    def authenticate(self, profile, interactive):
        pass

    def handle_error(self, exitcode: int, *logerror: Any):
        """If an error happens in libnss, handle it and print some debug information
        """
        if logerror:
            LOG.error(*logerror)
        else:
            LOG.debug("Error during a call to NSS library, trying to obtain error info")

        code = self._PORT_GetError()
        name = self._PR_ErrorToName(code)
        name = "NULL" if name is None else name
        # 0 is the default language (localization related)
        text = self._PR_ErrorToString(code, 0)

        LOG.debug("%s: %s", name, text)

        raise Exit(exitcode)

    def decrypt(self, data64):
        data = b64decode(data64)
        inp = self.SECItem(0, data, len(data))
        out = self.SECItem(0, None, 0)

        err_status: int = self._PK11SDR_Decrypt(inp, out, None)
        LOG.debug("Decryption of data returned %s", err_status)
        try:
            if err_status:  # -1 means password failed, other status are unknown
                self.handle_error(
                    Exit.NEED_MASTER_PASSWORD,
                    "Password decryption failed. Passwords protected by a Master Password!",
                )

            res = out.decode_data()
        finally:
            # Avoid leaking SECItem
            self._SECITEM_ZfreeItem(out, 0)

        return res


class MozillaInteraction:
    """
    Abstraction interface to Mozilla profile and lib NSS
    """

    def __init__(self):
        self.profile = None
        self.proxy = NSSProxy()

    def load_profile(self, profile):
        """Initialize the NSS library and profile
        """
        self.profile = profile
        self.proxy.initialize(self.profile)

    def authenticate(self, interactive):
        """Authenticate the the current profile is protected by a master password,
        prompt the user and unlock the profile.
        """
        self.proxy.authenticate(self.profile, interactive)

    def unload_profile(self):
        """Shutdown NSS and deactivate current profile
        """
        self.proxy.shutdown()

    def decrypt_passwords(self, credentials: []) -> dict:
        """Decrypt requested profile using the provided password.
        Returns all passwords in a list of dicts
        """
        decrypted_obj = {"Credentials": []}
        decrypted = decrypted_obj.get("Credentials")
        for credentials_obj in credentials:
            # enctype informs if passwords need to be decrypted
            enctype = credentials_obj.get("encType")
            domain = credentials_obj.get("formSubmitURL")
            username = credentials_obj.get("encryptedUsername")
            password = credentials_obj.get("encryptedPassword")
            if enctype:
                try:
                    username = self.proxy.decrypt(username)
                    password = self.proxy.decrypt(password)
                except (TypeError, ValueError) as e:
                    print(e)
                    continue
            decrypted.append({"url": domain, "username": username, "password": password})
        return decrypted_obj


class OutputFormat:
    def __init__(self, pwstore: PWStore, cmdargs: argparse.Namespace):
        self.pwstore = pwstore
        self.cmdargs = cmdargs

    def output(self):
        pass


def read_profiles(basepath):
    profileini = os.path.join(basepath, "profiles.ini")

    LOG.debug("Reading profiles from %s", profileini)

    if not os.path.isfile(profileini):
        LOG.warning("profile.ini not found in %s", basepath)
        raise Exit(Exit.MISSING_PROFILEINI)

    # Read profiles from Firefox profile folder
    profiles = ConfigParser()
    profiles.read(profileini, encoding=DEFAULT_ENCODING)

    LOG.debug("Read profiles %s", profiles.sections())

    return profiles


class ConvertChoices(argparse.Action):
    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, choices=choices.keys(), **kwargs)
        self.mapping = choices

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, self.mapping[value])


def setup_logging() -> None:
    """Setup the logging level and configure the basic logger
    """
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    global LOG
    LOG = logging.getLogger(__name__)


def identify_system_locale() -> str:
    encoding: Optional[str] = locale.getpreferredencoding()

    if encoding is None:
        LOG.error(
            "Could not determine which encoding/locale to use for NSS interaction. "
            "This configuration is unsupported.\n"
            "If you are in Linux or MacOS, please search online "
            "how to configure a UTF-8 compatible locale and try again."
        )
        raise Exit(Exit.BAD_LOCALE)

    return encoding


def handle_firefox_passwords(session_dir_path: pathlib.Path, credentials: dict) -> list:
    firefox_passwords = []
    setup_logging()
    moz = MozillaInteraction()
    moz.load_profile(session_dir_path)
    # Decode all passwords
    if credentials:
        passwords_object = moz.decrypt_passwords(credentials)
        for obj in passwords_object.get("Credentials"):
            firefox_passwords.append(
                {"url": obj.get("url"), "username": obj.get("username"), "password": obj.get("password")})
    return firefox_passwords


def handle_all_firefox_modules(session_dir_path: pathlib.Path, results: dict):
    firefox_product = _FIREFOX_PRODUCT
    firefox_passwords = results.get("Firefox-Passwords")
    firefox_product["Passwords"] = handle_firefox_passwords(session_dir_path, firefox_passwords.get("logins"))
    firefox_cookies = results.get("Firefox-Cookies")
    firefox_product["Cookies"] = handle_firefox_cookies(firefox_cookies)
    return firefox_product


def handle_firefox_cookies(cookies_arr: list) -> list:
    firefox_cookies = []
    for cookie_obj in cookies_arr:
        cookie_domain = cookie_obj.get("host")
        cookie_name = cookie_obj.get("name")
        cookie = cookie_obj.get("value")
        firefox_cookies.append({"domain": cookie_domain, "name": cookie_name, "cookie": cookie})
    return firefox_cookies
