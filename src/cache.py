class Cache:
    """
    Holds infomation for each discord server locally.
    To reduce queries to the database, commands set are sent to the database,
    otherwise the database is only queried on start up to populate cache.
    """

    def __init__(self):
        # internal variables
        self.now_playing_track = None
        self.playing_view = None
        self.playing_view_channel = None
        self.playing_view_message = None
        self.user_who_want_to_skip = []

        # database variables
        self.music_channel_id = None
        self.music_role_id = None
        self.volume = 25

    def __str__(self):
        return f"""
        now playing, {self.now_playing_track}
        playing view channel id, {self.playing_view_channel_id}
        playing view message id, {self.playing_view_message_id}
        playing_view, {self.playing_view}
        song queue, {self.queue}
        user who want to skip, {self.user_who_want_to_skip}

        music_channel_id, {self.music_channel_id}
        music_role_id, {self.music_role_id}
        volume, {self.volume}
        """
