class Cache:
    """
    Holds infomation for each discord server locally.
    To reduce queries to the database by doing one big read on startup.
    Writes to the database are wrote to the cache and the database.
    """

    def __init__(self):
        self.music_channel_id = None
        self.music_role_id = None
        self.volume = 25
