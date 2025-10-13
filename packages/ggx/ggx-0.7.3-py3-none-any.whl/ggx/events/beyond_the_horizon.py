import asyncio
from typing import Dict, Union
from loguru import logger
from ..client.game_client import GameClient


class BeyondTheHorizon(GameClient):
    """Beyond The Horizon operations handler."""

    async def get_bth_points(self, sync: bool = True) -> Union[Dict, bool]:
        """Retrieve Beyond The Horizon points."""
        try:
            if sync:
                return await self.send_rpc("tsh", {})
            else:
                await self.send_json_message("tsh", {})
                return True
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for BTH points response")
            return False
        except ConnectionError as e:
            logger.error(f"Connection error while getting BTH points: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while getting BTH points: {e}")
            return False

    async def choose_bth_castle(
        self,
        castle_id: int,
        only_rubies: int = 0,
        use_rubies: int = 0,
        sync: bool = True
    ) -> Union[Dict, bool]:
        """Choose castle in Beyond The Horizon."""
        try:
            castle_data = {"ID": castle_id, "OC2": only_rubies, "PWR": use_rubies, "GST": 3}
            if sync:
                return await self.send_rpc("tsc", castle_data)
            else:
                await self.send_json_message("tsc", castle_data)
                return True
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for BTH castle choice response")
            return False
        except ConnectionError as e:
            logger.error(f"Connection error while choosing BTH castle: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while choosing BTH castle: {e}")
            return False

    async def get_bth_token(self, sync: bool = True) -> Union[Dict, bool]:
        """Get Beyond The Horizon token."""
        try:
            token_data = {"GST": 3}
            if sync:
                return await self.send_rpc("glt", token_data)
            else:
                await self.send_json_message("glt", token_data)
                return True
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for BTH token response")
            return False
        except ConnectionError as e:
            logger.error(f"Connection error while getting BTH token: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while getting BTH token: {e}")
            return False

    async def login_bth(self, token: str, sync: bool = True) -> Union[Dict, bool]:
        """
        Login to BTH with token.
        Request cmd: 'tlep' → expected response cmd: 'lli'
        """
        try:
            data = {"TLT": token}
            if sync:
                # folosim crpc ca să așteptăm 'lli' după ce trimitem 'tlep'
                return await self.send_crpc("tlep", data, expect="lli")
            else:
                await self.send_json_message("tlep", data)
                return True
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for BTH login response")
            return False
        except ConnectionError as e:
            logger.error(f"Connection error while logging into BTH: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while logging into BTH: {e}")
            return False
