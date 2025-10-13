import asyncio
import json
import random
import json
import re
import inspect
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable, TypeAlias
import aiohttp
from loguru import logger
from websockets.asyncio.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosed

from ._cfg import *


class GameClient:
    
    HandlerType: TypeAlias = Callable[[Any], Union[Any, Awaitable[Any]]]
    
    def __init__(
        self,
        url: str,
        server_header: str,
        username: str,
        password: str
    ) -> None:
        
        self.url = url
        self.server_header = server_header
        self.username = username
        self.password = password
        
        self.ws: Optional[ClientConnection] = None
        self.connected = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._tasks: List[asyncio.Task] = []
        
        self._msg_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        # FIFO de futures per command
        self._pending_futures: Dict[str, deque[asyncio.Future]] = {}
        self.user_agent = random.choice(DEFAULT_UA_LIST)
        

    async def connect(self) -> None:
        """
        Main client loop to manage connection and reconnection.
        """
        reconnect_delay = 5
        max_reconnect_delay = 60
        
        while not self._stop_event.is_set():
            try:
                await self._run_connection_session()
                reconnect_delay = 5  # Reset delay on successful connection
                
            except (ConnectionClosed, asyncio.CancelledError):
                logger.warning("Connection closed gracefully.")
                self.connected.clear()
                if self._stop_event.is_set():
                    break
                    
            except Exception as e:
                logger.error(f"Error during connection session: {e}")
                self.connected.clear()
                if self._stop_event.is_set():
                    break
                    
            # Exponential backoff for reconnections
            if not self._stop_event.is_set():
                logger.info(f"Attempting to reconnect in {reconnect_delay} seconds...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
        
        logger.info("Client shutdown complete.")

    async def _run_connection_session(self) -> None:
        """
        Handles a single connection session.
        """
        async with connect(
            self.url,
            origin=CLIENT_ORIGIN,
            user_agent_header=self.user_agent,
            additional_headers=WS_HEADERS
        ) as ws:
            self.ws = ws
            self.connected.set()
            logger.info(f"GGClient connected! {VERSION}")
            
            # Create all tasks
            tasks = [
                asyncio.create_task(self._listener(), name="listener"),
                asyncio.create_task(self.keep_alive(), name="keep_alive"),
                asyncio.create_task(self._nch(), name="nch")
            ]
            
            if not await self._init():
                await self._cancel_tasks(tasks)
                await self.disconnect()
                return
            
            tasks.append(asyncio.create_task(self.run_jobs(), name="run_jobs"))
            self._tasks = tasks
            
            try:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_EXCEPTION,
                    timeout=None
                )
                
                # Check for exceptions in completed tasks
                for task in done:
                    if task.exception():
                        # Cancel all pending tasks before raising
                        for pending_task in pending:
                            if not pending_task.done():
                                pending_task.cancel()
                        # Wait for cancellation to complete
                        if pending:
                            await asyncio.gather(*pending, return_exceptions=True)
                        raise task.exception()
                        
            except Exception as e:
                logger.error(f"Task error: {e}")
                # Ensure all tasks are cancelled
                await self._cancel_tasks(tasks)
                raise
            finally:
                # Cleanup - make sure all tasks are done
                for task in tasks:
                    if not task.done():
                        task.cancel()
                # Wait for all tasks to finish
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _cancel_tasks(self, tasks: List[asyncio.Task]) -> None:
        """Cancel tasks gracefully."""
        for task in tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
                
    async def _init(self) -> bool:
        await self._init_socket()
        return await self.login(self.username, self.password)            
 
    async def run_jobs(self) -> None:
        """Override this method in subclasses to implement custom jobs."""
        while self.connected.is_set() and not self._stop_event.is_set():
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        self.connected.clear()
        self._cancel_pending_futures()
        
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.ws = None

        logger.info("Disconnected!.")
 
    async def shutdown(self) -> None:
        """Shutdown the client completely."""
        self._stop_event.set()
        await self.disconnect()
        
        
        
        current_task = asyncio.current_task()
        tasks_to_cancel = [t for t in self._tasks if t is not current_task and not t.done()]

        for task in tasks_to_cancel:
            task.cancel()
            
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

    async def send(self, message: str) -> None:
        """Send raw message to server."""
        if not self.ws or not self.connected.is_set():
            raise RuntimeError("GGClient not connected!")
        await self.ws.send(message)
 
    async def send_message(self, parts: List[str]) -> None:
        """Send formatted message with % separators."""
        msg = "%".join(["", *parts, ""])
        await self.send(msg)
 
    async def send_raw_message(self, command: str, data: List[Any]) -> None:
        """Send raw message with JSON serialization for complex types."""
        json_parts = [json.dumps(item) if isinstance(item, (dict, list)) else str(item) for item in data]
        await self.send_message(["xt", self.server_header, command, "1", *json_parts])

    async def send_json_message(self, command: str, data: Dict[str, Any]) -> None:
        """Send JSON message."""
        await self.send_message(["xt", self.server_header, command, "1", json.dumps(data)])

    async def send_xml_message(self, t: str, action: str, r: str, data: str) -> None:
        """Send XML message."""
        await self.send(f"<msg t='{t}'><body action='{action}' r='{r}'>{data}</body></msg>")
 
    async def receive(self) -> Dict[str, Any]:
        """Receive message from queue."""
        return await self._msg_queue.get()



    def _parse_message(self, message: str) -> Dict[str, Any]:
        if message.startswith("<"):
            m = re.search(r"<msg t='(.*?)'><body action='(.*?)' r='(.*?)'>(.*?)</body></msg>", message)
            t_val, action, r_val, data = m.groups()
            return {"type": "xml", "payload": {"t": t_val, "action": action, "r": int(r_val), "data": data}}
        
        parts = message.strip("%").split("%")
        cmd = parts[1]; status = int(parts[3])
        raw = "%".join(parts[4:])
        
        try:
            data = json.loads(raw)
        except:
            data = raw
        
        parsed_data = {"type": "json", "payload": {"command": cmd, "status": status, "data": data}}      
        return parsed_data


    async def _listener(self) -> None:
        """Improved message listener with better future management."""
        try:
            async for raw in self.ws:
                if self._stop_event.is_set():
                    break
                    
                text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                msg = self._parse_message(text)
                
                # Put message in queue (dacă ai consumatori externi)
                await self._msg_queue.put(msg)
                
                # Handle futures and callbacks
                await self._handle_message_callbacks(msg)
                
        except ConnectionClosed:
            logger.warning("Connection closed, stopping listener...")
            # Cancel all pending futures
            self._cancel_pending_futures()
        except asyncio.CancelledError:
            logger.warning("Listener task cancelled.")
            self._cancel_pending_futures()
        except Exception as e:
            logger.error(f"Unexpected error in listener: {e}")
            self._cancel_pending_futures()

    async def _handle_message_callbacks(self, msg: Dict[str, Any]) -> None:
        """Handle futures and callbacks for incoming messages."""
        payload = msg.get("payload", {})
        cmd = payload.get("command") or payload.get("action")
        
        if not cmd:
            return
            
        data = payload.get("data")
        status = payload.get("status")

        # Dacă protocolul tău folosește status==1 ca ACK/heartbeat, ignoră-l
        def is_final_response() -> bool:
            return (status is None) or (status != 1)
        
        # === Livrare FIFO: un răspuns -> un Future ===
        if cmd in self._pending_futures and is_final_response():
            q = self._pending_futures[cmd]
            while q:
                fut = q.popleft()
                if not fut.done():
                    fut.set_result(data)
                    break
            if not q:
                self._pending_futures.pop(cmd, None)
        
        # Handlers on_<cmd>
        method_name = f"on_{cmd}"
        if hasattr(self, method_name):
            handler = getattr(self, method_name)
            try:
                if inspect.iscoroutinefunction(handler):
                    asyncio.create_task(handler(data))
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in handler {method_name}: {e}")

    def _cancel_pending_futures(self) -> None:
        """Cancel all pending futures on disconnect."""
        for cmd, q in list(self._pending_futures.items()):
            while q:
                fut = q.popleft()
                if not fut.done():
                    fut.set_exception(ConnectionError("Connection lost"))
            self._pending_futures.pop(cmd, None)

    # --- helper pentru înregistrare înainte de send ---
    def _register_future(self, command: str) -> asyncio.Future:
        """Register a future for a command response."""
        fut = asyncio.get_running_loop().create_future()
        q = self._pending_futures.setdefault(command, deque())
        q.append(fut)
        return fut


           
    async def send_rpc(self, command: str, data: Dict[str, Any], timeout: float = 5.0) -> Any:
        """Send RPC with proper future handling (register before send)."""
        fut = self._register_future(command)  # înregistrăm ÎNAINTE de send
        await self.send_json_message(command, data)
        try:
            return await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            q = self._pending_futures.get(command)
            if q and fut in q:
                q.remove(fut)
                if not q:
                    self._pending_futures.pop(command, None)
            if not fut.done():
                fut.cancel()
            raise

    async def send_crpc(
        self,
        command: str,
        data: Dict[str, Any],
        expect: str,
        timeout: float = 5.0,
    ) -> Any:
        """Send RPC with proper future handling (register before send)."""
        fut = None
        try:
            fut = self._register_future(expect)
            await self.send_json_message(command, data)
            resp = await asyncio.wait_for(fut, timeout=timeout)
            return resp
        
        except asyncio.TimeoutError:
            q = self._pending_futures.get(expect)
            try:
                if q and fut in q:
                    q.remove(fut)
                    if not q:
                        self._pending_futures.pop(expect, None)
            except Exception:
                pass
            if fut and not fut.done():
                fut.cancel()
            logger.error(f"Timeout waiting for response '{expect}' after sending '{command}'")
            return False
        
        except ConnectionError as e:
            logger.error(f"Connection error during '{command}' -> '{expect}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in send_crpc({command}->{expect}): {e}")
            return False
        
        
    async def send_hrpc(self, command: str, data: Dict[str, Any], handler: HandlerType, timeout: float = 5.0) -> Any:
        """Send RPC with handler and FIFO future handling."""
        fut = self._register_future(command)  # înregistrăm ÎNAINTE de send
        await self.send_json_message(command, data)
        resp_data = await asyncio.wait_for(fut, timeout)
        to_handle = handler(resp_data)
        if inspect.isawaitable(to_handle):
            await to_handle
        return to_handle
       
    async def keep_alive(self, interval: int = 60) -> None:
        """Keep connection alive with periodic pings."""
        try:
            await self.connected.wait()
            while self.connected.is_set() and not self._stop_event.is_set():
                await asyncio.sleep(interval)
                try:
                    await self.send_raw_message("pin", ["<RoundHouseKick>"])
                except Exception as e:
                    logger.error(f"Error sending keep-alive: {e}")
                    break
        except asyncio.CancelledError:
            logger.warning("Keep-alive task cancelled.")

    async def _nch(self, interval: int = 360) -> None:
        """Periodic NCH message."""
        try:
            await self.connected.wait()
            while self.connected.is_set() and not self._stop_event.is_set():
                await asyncio.sleep(interval)
                try:
                    await self.send(f'%xt%{self.server_header}%nch%1%')
                except Exception as e:
                    logger.error(f"Error sending NCH: {e}")
                    break
        except asyncio.CancelledError:
            logger.warning("NCH task cancelled.")
        
    async def _init_socket(self):
        """Initialize socket connection."""
        try:
            await self.send_xml_message("sys", "verChk", "0", "<ver v='166' />")
            await self.send_xml_message("sys", "login", "0", 
                                        f"<login z='{self.server_header}'><nick><![CDATA[]]></nick><pword><![CDATA[1123010%fr%0]]></pword></login>")
            await self.send_xml_message("sys", "autoJoin", "-1", "")
            await self.send_xml_message("sys", "roundTrip", "1", "")
        except Exception as e:
            logger.error(f"Error during socket initialization: {e}")
            raise

    async def fetch_game_db(self) -> dict:
        async with aiohttp.ClientSession(headers=AD_HEADERS) as session:
            async with session.get(GAME_VERSION_URL) as resp:
                resp.raise_for_status()
                text = await resp.text()
                _, version = text.strip().split("=", 1)
                version = version.strip()
            
            db_url = f"https://empire-html5.goodgamestudios.com/default/items/items_v{version}.json"
            async with session.get(db_url) as db_resp:
                db_resp.raise_for_status()
                data = await db_resp.json()
                return data
            
    async def login(
        self,
        username: str,
        password: str
        ) -> bool:
        """Login to the game server using RPC handling."""
        
        if not self.connected.is_set():
            logger.error("Not connected yet!")
            return False
            
        try:
            data = {
                "CONM": 175,
                "RTM": 24,
                "ID": 0,
                "PL": 1,
                "NOM": username,
                "PW": password,
                "LT": None,
                "LANG": "fr",
                "DID": "0",
                "AID": "1674256959939529708",
                "KID": "",
                "REF": "https://empire.goodgamestudios.com",
                "GCI": "",
                "SID": 9,
                "PLFID": 1
            }
                
            response = await self.send_rpc("lli", data, timeout=5.0)

            if not isinstance(response, dict):
                logger.info("Login successful!")
                return True
                
            if isinstance(response, dict) and not response:
                logger.warning("Wrong username or password!")
                return False
                
            if isinstance(response, dict) and "CD" in response:
                cooldown_value = response["CD"]
                logger.debug(f'Connection locked by the server! Reconnect in {cooldown_value} sec!')
                await asyncio.sleep(cooldown_value)
                return False
            else:
                logger.info("Login successful!")
                return True
                 
        except asyncio.TimeoutError:
            logger.error("Login timeout - server not responding")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
        
        
 