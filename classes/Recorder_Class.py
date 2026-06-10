import pyaudio
import threading
import numpy as np


class AudioRecorder:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 88200
        self.is_recording = False
        self.frames = []
        self.p = None
        self.stream = None

    def start_recording(self):
        self.is_recording = True
        self.frames = []

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        # Запись в отдельном потоке
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def _record(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Ошибка записи: {e}")
                break

    def stop_recording(self):
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

        return b''.join(self.frames)

    def get_audio_bytes(self):
        audio_array = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        pygame_bytes = audio_array.tobytes()
        return pygame_bytes