import asyncio
import json
import random
import re
import inspect
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
        self._pending_futures: Dict[str, List[asyncio.Future]] = {}
        self.user_agent = random.choice(DEFAULT_UA_LIST)
        self._http_session: Optional[aiohttp.ClientSession] = None

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
            additional_headers=AD_HEADERS
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
        pass

    async def disconnect(self) -> None:
        self.connected.clear()
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        logger.info("Disconnected!.")
 
    async def shutdown(self) -> None:
        self._stop_event.set()
        await self.disconnect()
        
        # Close HTTP session if exists
        if self._http_session:
            await self._http_session.close()
        
        current_task = asyncio.current_task()
        tasks_to_cancel = [t for t in self._tasks if t is not current_task]

        for task in tasks_to_cancel:
            task.cancel()
            
        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

    async def send(self, message: str) -> None:
        if not self.ws:
            raise RuntimeError("GGClient not connected!")
        await self.ws.send(message)
 
    async def send_message(self, parts: List[str]) -> None:
        msg = "%".join(["", *parts, ""])
        await self.send(msg)
 
    async def send_raw_message(self, command: str, data: List[Any]) -> None:
        json_parts = [json.dumps(item) if isinstance(item, (dict, list)) else item for item in data]
        await self.send_message(["xt", self.server_header, command, "1", *json_parts])

    async def send_json_message(self, command: str, data: Dict[str, Any]) -> None:
        await self.send_message(["xt", self.server_header, command, "1", json.dumps(data)])

    async def send_xml_message(self, t: str, action: str, r: str, data: str) -> None:
        await self.send(f"<msg t='{t}'><body action='{action}' r='{r}'>{data}</body></msg>")
 
    async def receive(self) -> Dict[str, Any]:
        return await self._msg_queue.get()

    # Pre-compile regex patterns for better performance
    _XML_PATTERN = re.compile(r"<msg t='(.*?)'><body action='(.*?)' r='(.*?)'>(.*?)</body></msg>")

    def _parse_message(self, message: str) -> Dict[str, Any]:
        """Parse incoming messages with better performance."""
        if message.startswith("<"):
            return self._parse_xml_message(message)
        else:
            return self._parse_json_message(message)

    def _parse_xml_message(self, message: str) -> Dict[str, Any]:
        """Parse XML messages."""
        match = self._XML_PATTERN.match(message)
        if match:
            t_val, action, r_val, data = match.groups()
            return {
                "type": "xml", 
                "payload": {
                    "t": t_val, 
                    "action": action, 
                    "r": int(r_val), 
                    "data": data
                }
            }
        return {"type": "unknown", "payload": {"data": message}}

    def _parse_json_message(self, message: str) -> Dict[str, Any]:
        """Parse JSON messages."""
        try:
            parts = message.strip("%").split("%")
            if len(parts) < 5:
                return {"type": "malformed", "payload": {"data": message}}
                
            cmd, status = parts[1], int(parts[3])
            raw_data = "%".join(parts[4:])
            
            # Only attempt JSON parsing if it looks like JSON
            data = json.loads(raw_data) if raw_data and raw_data[0] in ('{', '[') else raw_data
            
            return {
                "type": "json", 
                "payload": {
                    "command": cmd, 
                    "status": status, 
                    "data": data
                }
            }
        except (ValueError, IndexError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse message: {e}")
            return {"type": "malformed", "payload": {"data": message}}

    async def _listener(self) -> None:
        """Improved message listener with better future management."""
        try:
            async for raw in self.ws:
                text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                msg = self._parse_message(text)
                
                # Put message in queue
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

    async def _handle_message_callbacks(self, msg: Dict[str, Any]) -> None:
        """Handle futures and callbacks for incoming messages."""
        payload = msg.get("payload", {})
        cmd = payload.get("command") or payload.get("action")
        
        # Handle pending futures - DO NOT pop, just process and clean up
        if cmd in self._pending_futures:
            futures = self._pending_futures[cmd]  # Do not pop!
            data = payload.get("data")
            
            completed_futures = []
            for fut in futures:
                if not fut.done():
                    fut.set_result(data)
                    completed_futures.append(fut)
            
            # Remove completed futures
            for fut in completed_futures:
                futures.remove(fut)
            
            # Clean up empty lists
            if not futures:
                del self._pending_futures[cmd]
        
        # Handle method callbacks
        method_name = f"on_{cmd}"
        if hasattr(self, method_name):
            handler = getattr(self, method_name)
            data = payload.get("data")
            
            try:
                if inspect.iscoroutinefunction(handler):
                    asyncio.create_task(handler(data))
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in handler {method_name}: {e}")

    def _cancel_pending_futures(self) -> None:
        """Cancel all pending futures on disconnect."""
        for cmd, futures in self._pending_futures.items():
            for fut in futures:
                if not fut.done():
                    fut.set_exception(ConnectionError("Connection lost"))
        self._pending_futures.clear()

    async def wait_for_response(self, command: str, timeout: float = 5.0) -> Any:
        """Wait for response with proper future registration."""
        future = asyncio.get_event_loop().create_future()
        
        # Register future for this command
        if command not in self._pending_futures:
            self._pending_futures[command] = []
        self._pending_futures[command].append(future)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Remove the future if timeout occurs
            if command in self._pending_futures and future in self._pending_futures[command]:
                self._pending_futures[command].remove(future)
                if not self._pending_futures[command]:
                    del self._pending_futures[command]
            raise
        finally:
            # Cleanup - remove future if still present
            if command in self._pending_futures and future in self._pending_futures[command]:
                self._pending_futures[command].remove(future)
                if not self._pending_futures[command]:
                    del self._pending_futures[command]
           
    async def send_rpc(self, command: str, data: Dict[str, Any], timeout: float = 5.0) -> Any:
        """Send RPC with proper future handling."""
        await self.send_json_message(command, data)
        return await self.wait_for_response(command, timeout)

    async def send_hrpc(self, command: str, data: Dict[str, Any], handler: HandlerType, timeout: float = 5.0) -> Any:
        """Send RPC with handler and proper future handling."""
        await self.send_json_message(command, data)
        resp_data = await self.wait_for_response(command, timeout)
        to_handle = handler(resp_data)
        if inspect.isawaitable(to_handle):
            await to_handle
        return to_handle
       
    async def keep_alive(self, interval: int = 60) -> None:
        try:
            await self.connected.wait()
            while self.connected.is_set() and not self._stop_event.is_set():
                await asyncio.sleep(interval)
                await self.send_raw_message("pin", ["<RoundHouseKick>"])
        except asyncio.CancelledError:
            logger.warning("Keep-alive task cancelled.")

    async def _nch(self, interval: int = 360) -> None:
        try:
            await self.connected.wait()
            while self.connected.is_set():
                await asyncio.sleep(interval)
                await self.send(f'%xt%{self.server_header}%nch%1%')
        except asyncio.CancelledError:
            logger.warning("NCH task cancelled.")
        
    async def _init_socket(self):
        await self.send_xml_message("sys", "verChk", "0", "<ver v='166' />")
        await self.send_xml_message("sys", "login", "0", 
                                        f"<login z='{self.server_header}'><nick><![CDATA[]]></nick><pword><![CDATA[1123010%fr%0]]></pword></login>")
        await self.send_xml_message("sys", "autoJoin", "-1", "")
        await self.send_xml_message("sys", "roundTrip", "1", "")

    async def fetch_game_db(self) -> dict:
        """Use connection pooling for HTTP requests."""
        if not self._http_session:
            self._http_session = aiohttp.ClientSession()
        
        try:
            async with self._http_session.get(GAME_VERSION_URL) as resp:
                resp.raise_for_status()
                text = await resp.text()
                _, version = text.strip().split("=", 1)
                version = version.strip()
            
            db_url = f"https://empire-html5.goodgamestudios.com/default/items/items_v{version}.json"
            async with self._http_session.get(db_url) as db_resp:
                db_resp.raise_for_status()
                return await db_resp.json()
                
        except Exception as e:
            logger.error(f"Error fetching game DB: {e}")
            raise
            
    async def login(
        self,
        username: str,
        password: str
        ) -> bool:
        
        if not self.connected.is_set():
            logger.error("Not connected yet!")
            return False
            
        while True:
            try:
                await self.send_json_message(
                    "lli",
                    {
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
                    )
                
                response = await self.wait_for_response("lli")
                
                if not isinstance(response, dict):
                    return True
                
                if isinstance(response, dict) and not response:
                    logger.warning("Wrong username or password!")
                    return False
                
                if isinstance(response, dict) and "CD" in response:
                    cooldown_value = response["CD"]
                    logger.debug(f'Connection locked by the server! Reconnect in {cooldown_value} sec!')
                    await asyncio.sleep(cooldown_value)
                    
                else:
                    return True
                 
            except Exception as e:
                logger.error(f"Error during login: {e}")
                return False