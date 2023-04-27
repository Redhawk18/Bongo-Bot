import wavelink

from typing import TYPE_CHECKING, Any, Union
from wavelink.enums import *
from wavelink.ext import spotify
from wavelink.tracks import *

class Custom_Player(wavelink.player.Player):
    """Exact wavelink player with lavalink plugin support for sponserblock"""
    async def play(self,
                   track: Playable,
                   replace: bool = True,
                   start: int | None = None,
                   end: int | None = None,
                   volume: int | None = None,
                   *,
                   populate: bool = False
                   ) -> Playable:
        """|coro|
        Play a WaveLink Track.
        Parameters
        ----------
        track: :class:`tracks.Playable`
            The :class:`tracks.Playable` track to start playing.
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
        populate: bool
            Whether to populate the AutoPlay queue. This is done automatically when AutoPlay is on.
            Defaults to False.
        Returns
        -------
        :class:`tracks.Playable`
            The track that is now playing.
        """
        assert self._guild is not None

        if isinstance(track, spotify.SpotifyTrack):
            track = await track.fulfill(player=self, cls=YouTubeTrack, populate=populate)

        data = {
            'encodedTrack': track.encoded,
            'position': start or 0,
            'volume': volume or self._volume,
            'skipSegments': ["interaction", "music_offtopic", "preview", "selfpromo", "sponsor"]
        }

        if end:
            data['endTime'] = end

        resp: dict[str, Any] = await self.current_node._send(method='PATCH',
                                                             path=f'sessions/{self.current_node._session_id}/players',
                                                             guild_id=self._guild.id,
                                                             data=data,
                                                             query=f'noReplace={not replace}')

        self._player_state['track'] = resp['track']['encoded']
        self._current = track

        return track

