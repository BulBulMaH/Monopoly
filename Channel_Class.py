import pygame as pg


class Channel:
    def __init__(self, id):

        self.channel = pg.mixer.Channel(id)
        self.is_paused = False
        self.audio_id = None

    def pause(self):
        self.channel.pause()
        self.is_paused = True

    def unpause(self):
        self.channel.unpause()
        self.is_paused = False

    def play(self, sound, audio_id):
        self.channel.play(sound)
        self.is_paused = False
        self.audio_id = audio_id

    def get_busy(self):
        return self.channel.get_busy()

    def get_sound(self):
        return self.channel.get_sound()