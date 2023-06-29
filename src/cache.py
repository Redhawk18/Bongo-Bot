class Cache:
    """
    Holds infomation for each discord server locally.
    To reduce queries to the database, commands set are sent to the database,
    otherwise the database is only queried on start up to populate cache.
    """

    def __init__(self):
        # internal variables
        self.playing_view = None
        self.playing_view_channel = None
        self.playing_view_message = None
        self.user_who_want_to_skip = []

        # database variables
        self.music_channel_id = None
        self.music_role_id = None
        self.volume = 25
