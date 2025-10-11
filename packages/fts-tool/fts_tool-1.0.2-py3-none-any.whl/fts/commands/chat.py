import asyncio
import random

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

import fts.core.secure as secure
from fts.config import DEFAULT_CHAT_PORT

# Predefined ANSI color codes
COLORS = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
]
RESET = "\033[0m"

# -------------------------
# Host a chatroom
# -------------------------
def cmd_create(args, logger):
    port = args.port or DEFAULT_CHAT_PORT
    host = "0.0.0.0"
    logger.debug(f"Starting FTS chatroom on {host}:{port}")
    logger.debug(f"Options: {args}")

    async def run_server_and_client():
        server_task = asyncio.create_task(
            start_server(host=host, port=port, logger=logger)
        )
        await asyncio.sleep(0.5)
        client_task = asyncio.create_task(
            client(host="127.0.0.1", port=port, name=args.name or "Host", logger=logger)
        )
        await asyncio.gather(server_task, client_task)

    # Try dynamic port handling BEFORE running asyncio
    for attempt in range(45):
        try:
            server_coro = run_server_and_client()
            asyncio.run(server_coro)
            return
        except OSError as e:
            if port != 0:
                logger.warning(f"Port {port} unavailable, retrying with free port...")
                port +=1
            else:
                logger.error(f"Failed to start server: {e}")
                return
        except KeyboardInterrupt:
            logger.info("Chatroom closed")
            return
        except Exception as e:
            logger.critical(f"Server error: {e}")
            return


# -------------------------
# Join a chatroom
# -------------------------
def cmd_join(args, logger):
    logger.debug(f"Options: {args}")

    host = args.ip
    port = args.port or DEFAULT_CHAT_PORT
    logger.info(f"Joining FTS chatroom at {host}:{port}")

    try:
        asyncio.run(client(host=host, port=port, name=args.name, logger=logger))
    except KeyboardInterrupt:
        logger.info("Disconnected from chatroom")


# -------------------------
# Server
# -------------------------
async def handle_client(reader, writer, clients, banned_ips, server_name, logger):
    user_name = None
    addr = writer.get_extra_info("peername")
    started = False
    user_color = None

    ip = addr[0]

    # Reject immediately if banned
    if ip in banned_ips:
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass
        return

    try:
        # --- 1. Wait for handshake ---
        while not started:
            data = await reader.readline()
            if not data:
                continue
            handshake = data.decode("utf-8", errors="replace").strip()
            if handshake:
                started = True
                user_name = handshake

                # --- ensure unique username ---
                existing_names = {info["name"] for info in clients.values()}

                while user_name in existing_names:
                    # if it already ends in a number, increment it
                    if user_name[-1].isdigit():
                        # split into prefix + number
                        prefix = user_name.rstrip("0123456789")
                        num_str = user_name[len(prefix):]
                        try:
                            num = int(num_str)
                        except ValueError:
                            num = 1
                        user_name = f"{prefix}{num + 1}"
                    else:
                        user_name = f"{user_name}2"

                # --- Assign a unique color ---
                used_colors = {info["color"] for info in clients.values()}
                available_colors = [c for c in COLORS if c not in used_colors]
                if available_colors:
                    user_color = random.choice(available_colors)
                else:
                    # fallback if all colors are used
                    user_color = random.choice(COLORS)


                ip = addr[0]
                clients[writer] = {"name": user_name, "color": user_color, "ip": ip}

                # broadcast join
                for w, info in clients.items():
                    if w is not writer:
                        try:
                            w.write(f"[+] {user_color}{user_name}{RESET} has joined the chat\n".encode())
                            await w.drain()
                        except:
                            pass
                break

        # --- 2. Main chat loop ---
        while data := await reader.readline():
            message = data.decode("utf-8", errors="replace").strip()
            if not message:
                continue

            if str(ip) == "127.0.0.1" and "!kick" in message:
                try:
                    target_name = message.split(" ", 1)[1].strip()
                    target = None

                    # Find target by name
                    for w, info in list(clients.items()):
                        if info["name"] == target_name:
                            target = (w, info)
                            break

                    if target:
                        tw, tinfo = target
                        banned_ips.add(tinfo["ip"])
                        # Notify everyone
                        for w2, info2 in list(clients.items()):
                            try:
                                w2.write(
                                    f"[!] {tinfo['color']}{tinfo['name']}{RESET} was kicked by admin\n".encode()
                                )
                                await w2.drain()
                            except:
                                clients.pop(w2, None)

                        # Close target’s connection
                        clients.pop(tw, None)
                        tw.close()
                        await tw.wait_closed()
                    else:
                        # feedback to admin only
                        logger.info(f"No such user: {target_name}\n")
                        continue

                except:
                    logger.info(f"Failed to parse command: {message}\n")
                    continue
            elif str(ip) == "127.0.0.1" and '!' == str(message[0]):
                    logger.info(f"Unknown command: {message}\n")
                    continue

            else:
                # broadcast to all clients except sender
                for w, info in list(clients.items()):
                    try:
                        w.write(f"[{user_color}{user_name}{RESET}] {message}\n".encode())
                        await w.drain()
                    except (ConnectionResetError, BrokenPipeError):
                        clients.pop(w, None)

    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        if started:
            clients.pop(writer, None)
            # broadcast leave
            for w, info in list(clients.items()):
                try:
                    w.write(f"[-] {user_color}{user_name}{RESET} has left the chat\n".encode())
                    await w.drain()
                except (ConnectionResetError, BrokenPipeError):
                    clients.pop(w, None)

        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass

async def start_server(host="0.0.0.0", port=DEFAULT_CHAT_PORT, server_name="FTS Server", logger=None):
    clients = {}  # writer -> username
    ssl_ctx = secure.get_server_context()
    banned_ips = set()

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, clients, banned_ips, server_name, logger),
        host, port,
        ssl=ssl_ctx
    )
    logger.info(f"FTS Chatroom listening on {host}:{port}(TLS)\n")

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            return


# -------------------------
# Client
# -------------------------
async def send(writer: asyncio.StreamWriter, logger):
    session = PromptSession("> ")
    try:
        while True:
            with patch_stdout():
                msg = await session.prompt_async()

            # Clear the input line after sending
            # Move cursor up one line and clear it
            print("\033[F\033[K", end='')

            if not msg:
                continue

            writer.write((msg + "\n").encode())
            await writer.drain()

    except (EOFError, asyncio.CancelledError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def listen(reader: asyncio.StreamReader, logger):
    from prompt_toolkit.patch_stdout import patch_stdout
    try:
        while data := await reader.readline():
            try:
                msg = data.decode('utf-8').rstrip()
            except Exception:
                continue

            if msg and any(32 <= ord(c) <= 126 for c in msg):
                # Use patch_stdout to allow ANSI colors to display correctly
                with patch_stdout():
                    logger.info(msg)

    except asyncio.IncompleteReadError:
        with patch_stdout():
            logger.info("Server closed connection")
    except asyncio.CancelledError:
        pass

async def client(host="127.0.0.1", port=DEFAULT_CHAT_PORT, name="Guest", logger=None):
    unique_name = name  # no random suffix

    async def establish_connection():
        reader, writer = await secure.connect_with_tofu_async(host, port, logger)
        logger.info(f"Connected to FTS chatroom at {host}:{port}\n")
        writer.write(f"{unique_name}\n".encode())
        await writer.drain()
        return reader, writer

    while True:
        try:
            reader, writer = await establish_connection()

            tasks = [
                asyncio.create_task(listen(reader, logger)),
                asyncio.create_task(send(writer, logger)),
                asyncio.create_task(heartbeat(writer, logger)),
            ]

            try:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            except KeyboardInterrupt:
                logger.info("Disconnecting from chatroom...")
                for t in tasks:
                    t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                break

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            for task in done:
                if task.exception():
                    raise task.exception()

        except (ConnectionResetError, BrokenPipeError):
            # Clear prompt line before logging
            print("\033[F\033[K", end='')  # move up & clear line
            with patch_stdout():
                logger.warning("Lost connection to server, reconnecting...\n")
            await asyncio.sleep(3)
        except Exception as e:
            print("\033[F\033[K", end='')
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(3)


# -------------------------
# Heartbeat
# -------------------------
async def heartbeat(writer: asyncio.StreamWriter, logger, interval: int = 1, max_failures: int = 3):
    failures = 0
    while True:
        try:
            await asyncio.sleep(interval)
            writer.write(b"\n")
            await writer.drain()
            failures = 0
        except (ConnectionResetError, BrokenPipeError):
            failures += 1
            if failures >= max_failures:
                raise
        except asyncio.CancelledError:
            break
