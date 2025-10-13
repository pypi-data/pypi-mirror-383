from cogworks.component import Component
from cogworks.components.camera import Camera
from cogworks.components.audio_source import AudioSource


class AudioListener(Component):
    def __init__(self):
        super().__init__()
        self._sources = set()

    def register_source(self, source: AudioSource) -> None:
        self._sources.add(source)
        source._listener = self

    def unregister_source(self, source: AudioSource) -> None:
        self._sources.discard(source)
        source._listener = None

    def clear_sources(self) -> None:
        for source in list(self._sources):
            source.stop()
            source._listener = None
        self._sources.clear()

    def update(self, dt: float) -> None:
        cam = self.game_object.get_component(Camera)
        if cam:
            listener_pos = (cam.offset_x, cam.offset_y)
            for source in list(self._sources):
                source.set_listener_position(listener_pos)
