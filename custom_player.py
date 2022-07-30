import wavelink

import contextlib
import datetime
import logging
from typing import Any, Dict, Union, Optional

import discord
from discord.channel import VoiceChannel

from wavelink import abc
from wavelink import Node, NodePool
from wavelink import WaitQueue
from wavelink import PartialTrack
#from wavelink import MISSING
from wavelink import Filter

class Custom_Player(wavelink.player.Player):
    """Exact wavelink player with lavalink plugin support for sponserblock"""
    async def play(
        self,
        source: abc.Playable,
        replace: bool = True,
        start: Optional[int] = None,
        end: Optional[int] = None,
        volume: Optional[int] = None,
        pause: Optional[bool] = None,
    ):
        """|coro|

        Play a WaveLink Track.

        Parameters
        ----------
        source: :class:`abc.Playable`
            The :class:`abc.Playable` track to start playing.
        replace: bool
            Whether this track should replace the current track. Defaults to ``True``.
        start: Optional[int]
            The position to start the track at in milliseconds.
            Defaults to ``None`` which will start the track at the beginning.
        end: Optional[int]
            The position to end the track at in milliseconds.
            Defaults to ``None`` which means it will play until the end.
        volume: Optional[int]
            Sets the volume of the player. Must be between ``0`` and ``1000``.
            Defaults to ``None`` which will not change the volume.
        pause: bool
            Changes the players pause state. Defaults to ``None`` which will not change the pause state.

        Returns
        -------
        :class:`wavelink.abc.Playable`
            The track that is now playing.
        """

        if not replace and self.is_playing():
            return

        await self.update_state({"state": {}})

        if isinstance(source, PartialTrack):
            source = await source._search()

        self._source = source

        payload = {
            "op": "play",
            "guildId": str(self.guild.id),
            "track": source.id,
            "noReplace": not replace,
            "skipSegments": [
                "interaction", "music_offtopic", "preview", "selfpromo", "sponsor"
            ]
        }
        if start is not None and start > 0:
            payload["startTime"] = str(start)
        if end is not None and end > 0:
            payload["endTime"] = str(end)
        if volume is not None:
            self._volume = volume
            payload["volume"] = str(volume)
        if pause is not None:
            self._paused = pause
            payload["pause"] = pause

        await self.node._websocket.send(**payload)

        #logger.debug(f"Started playing track:: {str(source)} ({self.channel.id})")
        return source
