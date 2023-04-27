from collections import deque

class Server_Infomation():
    """Holds infomation for each discord server the bot is added on"""

    def __init__(self):
        #internal variables
        self.song_queue = deque()
        self.is_playing = False
        self.playing_view_channel_id = None
        self.playing_view_message_id = None
        self.user_who_want_to_skip = []
        self.now_playing_track = None
        self.loop_enabled = False

        #database variables
        self.music_channel_id = None
        self.music_role_id = None
        self.volume:int = 25

    def __str__(self):
        return f"""
        song queue, {self.song_queue}
        is playing, {self.is_playing}
        playing view channel id, {self.playing_view_channel_id}
        playing view message id, {self.playing_view_message_id}
        user who want to skip, {self.user_who_want_to_skip}
        now playing, {self.now_playing_track}
        looping, {self.loop_enabled}
        
        music_channel_id, {self.music_channel_id}
        music_role_id, {self.music_role_id}
        volume, {self.volume}
        """
