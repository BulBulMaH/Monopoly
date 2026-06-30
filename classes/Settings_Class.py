import json
import pygame
import os


class Settings:
    def __init__(self):
        self.resolution_index = 1
        self.resolution_folder = '720p'
        self.max_fps = 60
        self.FPS = self.max_fps
        self.minimize_fps_optimize = False
        self.minimize_fps = 15
        self.inactive_fps_optimize = False
        self.inactive_fps = 30
        self.background_color = [128, 128, 128, 255]
        self.background_color_converted = pygame.Color(self.background_color)
        self.fullscreen = False
        self.scaled = False
        self.debug = False
        self.name = ''
        self.address = ''
        self.port = ''
        self.currency = 'default'

    def load_settings(self):
        default_settings = {'resolution index': 1,
                            'fps': 60,
                            'minimize window fps optimize': False,
                            'minimize window fps optimization value': 15,
                            'inactive fps optimize': False,
                            'inactive fps optimization value': 30,
                            'background color': [128, 128, 128, 255],
                            'fullscreen': False,
                            'scaled fullscreen': False,
                            'debug mode': False,
                            'name': '',
                            'address': '',
                            'port': '',
                            'currency': 'default'}

        if os.path.exists('settings.json'):
            with open('settings.json') as f:
                settings_data = json.load(f)
            for key in default_settings.keys():
                if key not in settings_data:
                    settings_data[key] = default_settings[key]
        else:
            settings_data = default_settings
            with open('settings.json', 'w') as outfile:
                json.dump(settings_data, outfile, indent=4, ensure_ascii=False)

        self.resolution_index = settings_data['resolution index']
        self.max_fps = settings_data['fps']
        self.background_color = settings_data['background color']
        self.fullscreen = settings_data['fullscreen']
        self.minimize_fps_optimize = settings_data['minimize window fps optimize']
        self.minimize_fps = settings_data['minimize window fps optimization value']
        self.inactive_fps_optimize = settings_data['inactive fps optimize']
        self.inactive_fps = settings_data['inactive fps optimization value']
        self.debug = settings_data['debug mode']
        self.name = settings_data['name']
        self.address = settings_data['address']
        self.port = settings_data['port']
        self.currency = settings_data['currency']

        if self.resolution_index == 1:
            self.resolution_folder = '720p'
        elif self.resolution_index == 2:
            self.resolution_folder = '1080p'
        elif self.resolution_index == 3:
            self.resolution_folder = '1440p'

        self.background_color_converted = pygame.Color(self.background_color)

        if not self.fullscreen:
            self.scaled = False

        if not self.inactive_fps_optimize:
            self.FPS = self.max_fps
        else:
            self.FPS = self.inactive_fps

    def save_settings(self):

        if self.resolution_index == 1:
            self.resolution_folder = '720p'
        elif self.resolution_index == 2:
            self.resolution_folder = '1080p'
        elif self.resolution_index == 3:
            self.resolution_folder = '1440p'

        self.background_color_converted = pygame.Color(self.background_color)

        if not self.fullscreen:
            self.scaled = False

        if not self.inactive_fps_optimize:
            self.FPS = self.max_fps
        else:
            self.FPS = self.inactive_fps

        settings_data_new = {'resolution index': self.resolution_index,
                             'fps': self.max_fps,
                             'minimize window fps optimize': self.minimize_fps_optimize,
                             'minimize window fps optimization value': self.minimize_fps,
                             'inactive fps optimize': self.inactive_fps_optimize,
                             'inactive fps optimization value': self.inactive_fps,
                             'background color': self.background_color,
                             'fullscreen': self.fullscreen,
                             'scaled fullscreen': self.scaled,
                             'debug mode': self.debug,
                             'name': self.name,
                             'address': self.address,
                             'port': self.port,
                             'currency': self.currency}

        with open('settings.json', 'w') as outfile:
            json.dump(settings_data_new, outfile, indent=4, ensure_ascii=False)
