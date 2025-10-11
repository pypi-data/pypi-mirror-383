#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import io
import os
import pathlib
import random
import string
import sys
from contextlib import redirect_stdout, redirect_stderr

import argui
from argui.types import FileSelectDir

from fts.core.aliases import resolve_alias
from fts.core.defaults import load_defaults
from fts.core.logger import setup_logging
from fts.core.secure import is_public_network


def size_type(value: str) -> int:
    """Parse human-readable sizes like '10MB' into bytes."""
    units = {"B":1, "KB":1024, "MB":1024**2, "GB":1024**3, "TB":1024**4, "PB":1024**5}
    value = value.upper().strip()
    for unit in units:
        if value.endswith(unit):
            num = float(value[:-len(unit)])
            return int(num * units[unit])
    return int(value)

# --- Lazy command loader with caching ---
_command_cache = {}

def load_cmd(module_path, func_name):
    """Lazy loader for commands, imports on first use and caches the function."""
    def wrapper(args, logger):
        key = (module_path, func_name)
        if key not in _command_cache:
            try:
                mod = __import__(module_path, fromlist=[func_name])
                _command_cache[key] = getattr(mod, func_name)
            except (ImportError, AttributeError) as e:
                logger.error(
                    "Failed to load command. Your install may be corrupted.\n"
                    "Run 'fts update --repair' or reinstall.\n"
                    f"{e}"
                )
                sys.exit(1)
        return _command_cache[key](args, logger)
    return wrapper


# --- Reusable argument groups ---
def add_log_flags(parser: argparse.ArgumentParser, defaults) -> None:
    """Add common logging and output flags."""

    parser.add_argument(
        "--logfile",
        metavar="FILE",
        type=pathlib.Path,
        help="Log output to a file",
        default=defaults.get("logfile", None),
    )

    #group = parser.add_mutually_exclusive_group()
    group = parser
    group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-critical output"
    )
    group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug output"
    )


def add_network_flags(parser: argparse.ArgumentParser, defaults) -> None:
    """Add network-related flags."""
    parser.add_argument(
        "-p", "--port",
        type=int,
        metavar="PORT",
        help="Override port used (0-65535)"
    )
    parser.add_argument(
        "--ip",
        metavar="ADDR",
        type=str,
        help="restrict requests to IP or hostname"
    )


# --- Main parser ---
def create_parser(gui=False) -> argparse.ArgumentParser:
    defaults = {}
    try:
        defaults = load_defaults()
    except Exception as e:
        print(f"Failed to load defaults: {e}", file=sys.stderr)

    parser = argparse.ArgumentParser(
        prog="fts",
        description="FTS: File transfers, chatrooms, and more."
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="COMMAND",
        help="Available commands",
    )

    add_log_flags(parser, defaults)

    # --- open ---
    open_parser = subparsers.add_parser(
        "open",
        help="Start a server and listen for incoming transfers"
    )
    open_parser.add_argument(
        "output",
        type=FileSelectDir(),
        metavar="OUTPUT_PATH",
        nargs="?",
        help="Directory to save incoming transfers - required",
        default=defaults.get("output", None),
    )
    open_parser.add_argument(
        "-d", "--detached",
        action="store_true",
        help="Run server in the background",
    )
    open_parser.add_argument(
        "-l", "--limit",
        type=str,
        metavar="SIZE",
        help="Transfer rate limit (e.g. 500KB, 2MB, 1GB)"
    )
    #open_parser.add_argument(
    #    "-t", "--timeout",
    #    type=int,
    #    metavar="SECONDS",
    #    help="Maximum time to wait for connection"
    #)
    open_parser.add_argument(
        "-x", "--extract",
        action="store_true",
        help="Automatically extract transferred archives"
    )
    open_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bars during operations"
    )
    add_network_flags(open_parser, defaults)
    open_parser.set_defaults(func=load_cmd("fts.commands.server", "cmd_open"))

    # --- send ---
    send_parser = subparsers.add_parser(
        "send",
        help="Send a file to a target host"
    )
    send_parser.add_argument(
        "path",
        type=pathlib.Path,
        help="Path to the file to send - required"
    )
    send_parser.add_argument(
        "ip",
        type=str,
        help="Target IP address or hostname - required"
    )
    send_parser.add_argument(
        "-n", "--name",
        type=str,
        help="Name to send file as"
    )
    send_parser.add_argument(
        "-p", "--port",
        type=int,
        help="Override port used"
    )
    send_parser.add_argument(
        "-l", "--limit",
        type=str,
        metavar="SIZE",
        help="Transfer rate limit (e.g. 500KB, 2MB, 1GB)"
    )
    send_parser.add_argument(
        "--nocompress",
        action="store_true",
        help="Skip compression (faster but larger transfer)"
    )
    send_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bars during operations"
    )
    send_parser.set_defaults(func=load_cmd("fts.commands.sender", "cmd_send"))

    # --- send-dir ---
    if gui:
        name = "senddir"
    else:
        name = "send-dir"
    send_dir_parser = subparsers.add_parser(
        name,
        help="Send a directory recursively"
    )
    send_dir_parser.add_argument(
        "path",
        type=FileSelectDir(),
        help="Directory to send - required"
    )
    send_dir_parser.add_argument(
        "ip",
        type=str,
        help="Target IP address or hostname - required"
    )
    send_dir_parser.add_argument(
        "-n", "--name",
        type=str,
        help="Name to send directory as"
    )
    send_dir_parser.add_argument(
        "-p", "--port",
        type=int,
        help="Override port used"
    )
    send_dir_parser.add_argument(
        "-l", "--limit",
        type=str,
        metavar="SIZE",
        help="Transfer rate limit (e.g. 500KB, 2MB, 1GB)"
    )
    send_dir_parser.add_argument(
        "--pyzip",
        action="store_true",
        help="use Python’s built-in compression instead of OS-level compression"
    )
    send_dir_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bars during operations"
    )
    send_dir_parser.set_defaults(func=load_cmd("fts.commands.sender", "cmd_send_dir"))

    # --- close ---
    close_parser = subparsers.add_parser(
        "close",
        help="Close a detached server",
    )
    close_parser.add_argument("process", choices=["all", "receiving", "library"], help="process to close")
    close_parser.set_defaults(func=load_cmd("fts.core.detatched", "cmd_close"))

    # --- trust ---
    if not gui:
        # --- version ---
        version_parser = subparsers.add_parser(
            "version",
            help="Show FTS version information"
        )
        version_parser.set_defaults(func=load_cmd("fts.commands.misc", "cmd_version"))

    trust_parser = subparsers.add_parser(
        "trust",
        help="Trust an IP certificate"
    )
    trust_parser.add_argument(
        "ip",
        type=str,
        help="IP address whose certificate should be trusted - required"
    )
    trust_parser.set_defaults(func=load_cmd("fts.core.secure", "cmd_clear_fingerprint"))

    # --- chat ---
    # chat create
    if gui:
        name = "chatcreate"
    else:
        name = "chat-create"
    chat_create_parser = subparsers.add_parser(name, help="create a new chatroom")
    chat_create_parser.add_argument("name", type=str, help="your username - required")
    chat_create_parser.add_argument("-p", "--port", type=int, help="Override port used")
    chat_create_parser.set_defaults(func=load_cmd("fts.commands.chat", "cmd_create"))

    # chat join
    if gui:
        name = "chatjoin"
    else:
        name = "chat-join"
    chat_create_parser = subparsers.add_parser(name, help="join an existing chatroom")
    chat_create_parser.add_argument("name", type=str, help="your username - required")
    chat_create_parser.add_argument("ip", type=str, help="IP to join - required")
    chat_create_parser.add_argument("-p", "--port", type=int, help="Override port used")
    chat_create_parser.set_defaults(func=load_cmd("fts.commands.chat", "cmd_join"))

    # --- library ---
    library_parser = subparsers.add_parser("library", help="download and manage local file directories!")
    library_parser.add_argument("task", choices=["find", "open", "manage"], help="task to perform")
    library_parser.add_argument(
        "output",
        type=FileSelectDir(),
        nargs="?",
        metavar="OUTPUT_PATH",
        help="Directory to save incoming transfers - required for (required for 'find')",
        default=defaults.get("output", None),
    )
    library_parser.add_argument(
        "-d", "--detached",
        action="store_true",
        help="Run server in the background (used in 'open')",
    )
    library_parser.set_defaults(func=load_cmd("fts.library.commands", "cmd_library"))

    # --- alias ---
    alias_parser = subparsers.add_parser("alias", help="manage aliases")
    alias_parser.add_argument("action", choices=["add", "remove", "list"], help="action to perform")
    alias_parser.add_argument("name", nargs="?", type=str, help="alias name (required for 'add/remove')")
    alias_parser.add_argument("value", nargs="?", type=str, help="alias value (required for 'add')")
    alias_parser.add_argument("type", nargs="?", type=str, choices=["ip", "dir"],
                              help="type of alias (required for 'add')")
    alias_parser.set_defaults(func=load_cmd("fts.core.aliases", "cmd_alias"))

    # --- defaults ---
    defaults_parser = subparsers.add_parser("defaults", help="manage default settings")
    defaults_parser.add_argument(
        "output",
        type=FileSelectDir(),
        metavar="OUTPUT_PATH",
        nargs="?",
        help="Directory to save incoming transfers - required",
        default=defaults.get("output", None),
    )

    defaults_parser.set_defaults(func=load_cmd("fts.core.defaults", "cmd_save"))

    return parser


def run(args):
    if args.verbose and args.quiet:
        print("ERROR: Verbose cannot be used with quiet!")
        return

    # --- Setup logger ---
    logfile = getattr(args, "logfile", None)
    log_created = False
    id=None
    if logfile:
        logfile = resolve_alias(logfile, "dir", logger=None)
        try:
            os.makedirs(os.path.dirname(os.path.abspath(logfile)), exist_ok=True)
            if not os.path.exists(logfile):
                open(logfile, "a").close()
                log_created = True
        except Exception as e:
            print(f"Warning: Could not create logfile '{logfile}': {e}")
            logfile = None

        try:
            alphabet = string.ascii_letters + string.digits
            number = ''.join(random.choices(alphabet, k=6))
            id = f"({args.command}|{number})"
        except Exception as e:
            print(f"Warning: Could not create id: {e}")

    # Determine logging mode based on command
    if "chat" in args.command:
        log_mode = "ptk"  # Use prompt_toolkit mode for chat
    else:
        log_mode = "tqdm"  # Default tqdm-compatible mode

    logger = setup_logging(
        verbose=getattr(args, "verbose", False),
        quiet=getattr(args, "quiet", False),
        logfile=logfile,
        mode=log_mode,
        id=id,
    )
    if log_created:
        logger.info(f"Log file created: {logfile}")

    # --- Resolve aliases ---
    if getattr(args, "output", None):
        args.output = resolve_alias(args.output, "dir", logger=logger)
    if getattr(args, "path", None):
        args.path = resolve_alias(args.path, "dir", logger=logger)
    if getattr(args, "ip", None):
        args.ip = resolve_alias(args.ip, "ip", logger=logger)

    # --- Enforce Alias ---
    #if "alias" in args.command and args.action == "add" and not args.type:
    #    logger.error("'alias add' requires a type argument ('ip' or 'dir').\n")
    #    sys.exit(2)
    #if "alias" in args.command and (args.action == "add" or args.action == "remove") and not args.name:
    #    logger.error("'alias add/remove' requires a name argument.\n")
    #    sys.exit(2)

    # --- Run selected command ---
    try:
        args.func(args, logger)
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
    print('')

def ensure_func(args):
    if hasattr(args, "func"):
        return args
    # map command -> (module, func_name)
    mapping = {
        "open": ("fts.commands.server", "cmd_open"),
        "send": ("fts.commands.sender", "cmd_send"),
        "senddir": ("fts.commands.sender", "cmd_send_dir"),
        "send-dir": ("fts.commands.sender", "cmd_send_dir"),
        "close": ("fts.core.detatched", "cmd_close"),
        "version": ("fts.commands.misc", "cmd_version"),
        "trust": ("fts.core.secure", "cmd_clear_fingerprint"),
        "alias": ("fts.core.aliases", "cmd_alias"),
        "chatcreate": ("fts.commands.chat", "cmd_create"),
        "chat-create": ("fts.commands.chat", "cmd_create"),
        "chatjoin": ("fts.commands.chat", "cmd_join"),
        "chat-join": ("fts.commands.chat", "cmd_join"),
        "library": ("fts.library.commands", "cmd_library"),
        "defaults": ("fts.core.defaults", "cmd_save"),
    }

    if args.command in mapping:
        mod, fn = mapping[args.command]
        args.func = load_cmd(mod, fn)

    return args


# Dummy sys.exit to prevent process termination
def dummy_exit(code=0):
    raise RuntimeError(f"sys.exit({code}) called")


# --- Main CLI setup ---
def main():
    if is_public_network("-v" in sys.argv or "--verbose" in sys.argv):
        print('FTS is disabled on public network\n')
        sys.exit(0)

    import logging
    gui = False

    if len(sys.argv) == 2:
        if "-v" in sys.argv:
            sys.argv.remove("-v")
        if "--verbose" in sys.argv:
            sys.argv.remove("--verbose")

    if len(sys.argv) == 1:
        sys.argv.extend(["--gui"])
        gui = True

    parser = create_parser(gui)
    interface = argui.Wrapper(parser, logLevel= logging.CRITICAL, )

    selected_cmd = False

    # Dummy output streams to collect prints for Command* error
    f = io.StringIO()
    args = None

    if gui:
        with redirect_stdout(f), redirect_stderr(f):
            while not selected_cmd:
                try:
                    args = interface.parseArgs()
                    if "No nodes match" in str(f.getvalue()):
                        f.seek(0)  # Move the cursor to the beginning of the stream
                        f.truncate(0)  # Truncate the stream to zero length
                        continue
                    else:
                        selected_cmd = True
                except:
                    break
    else:
        args = interface.parseArgs()

    if not args:
        print('')
        return

    try:
        run(ensure_func(args))
    except Exception as e:
        print(f"failed to run command: {e}")

if __name__ == "__main__":
    main()
