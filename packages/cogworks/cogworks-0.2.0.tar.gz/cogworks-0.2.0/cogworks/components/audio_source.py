import pygame
from cogworks.component import Component
from cogworks.utils.asset_loader import load_user_audio


class AudioSource(Component):
    def __init__(self):
        super().__init__()
        self.clip_path: str | None = None
        self.clip: pygame.mixer.Sound | None = None
        self.channel: pygame.mixer.Channel | None = None
        self.loop: bool = False
        self.volume: float = 1.0
        self.position: tuple[float, float] = (0.0, 0.0)
        self.listener_position: tuple[float, float] = (0.0, 0.0)
        self.max_distance: float = 5000.0
        self.auto_update_position: bool = True
        self._listener = None

    def start(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        listener = self.game_object.scene.get_active_audio_listener()
        if listener:
            listener.register_source(self)
            self._listener = listener

    def on_disabled(self) -> None:
        if self._listener:
            self._listener.unregister_source(self)
            self._listener = None
        self.stop()

    def on_remove(self) -> None:
        if self._listener:
            self._listener.unregister_source(self)
            self._listener = None
        self.stop()

    def update(self, dt: float) -> None:
        if self.auto_update_position:
            self.position = self.game_object.transform.get_world_position()
        self.update_spatial_audio()

    def set_clip(self, relative_path: str) -> None:
        self.clip_path = relative_path
        self.clip = load_user_audio(relative_path)
        self.clip.set_volume(self.volume)

    def play(self, bypass_spatial: bool = False) -> None:
        """Play the assigned clip, optionally bypassing distance attenuation."""
        if not self.clip:
            return

        loops = -1 if self.loop else 0
        self.channel = self.clip.play(loops=loops)
        if self.channel:
            if bypass_spatial:
                self.channel.set_volume(self.volume, self.volume)
        else:
            print(f"[AudioSource] Failed to play '{self.clip_path}'")

    def play_one_shot(self, relative_path: str, volume: float = 1.0, bypass_spatial: bool = False) -> None:
        """
        Play a single audio clip once without affecting the main clip.

        Args:
            relative_path (str): Path to the audio file.
            volume (float): Volume multiplier (0.0 - 1.0)
            bypass_spatial (bool): If True, play at full volume ignoring listener distance.
        """
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        try:
            clip = load_user_audio(relative_path)
            clip.set_volume(max(0.0, min(1.0, volume)))
            channel = clip.play()
            if channel:
                if bypass_spatial:
                    channel.set_volume(volume, volume)
            else:
                print(f"[AudioSource] Failed to PlayOneShot '{relative_path}'")
        except Exception as e:
            print(f"[AudioSource] Error playing one-shot '{relative_path}': {e}")

    def stop(self) -> None:
        if self.channel:
            self.channel.stop()
            self.channel = None

    def set_listener_position(self, pos: tuple[float, float]) -> None:
        self.listener_position = pos

    def update_spatial_audio(self) -> None:
        if not self.channel:
            return

        sx, sy = self.position
        lx, ly = self.listener_position

        dx = sx - lx
        dy = sy - ly
        distance = (dx**2 + dy**2) ** 0.5

        attenuation = max(0.0, 1.0 - (distance / self.max_distance))
        total_volume = self.volume * attenuation

        pan = max(-1.0, min(1.0, dx / self.max_distance))
        left = total_volume * (1.0 - max(0, pan))
        right = total_volume * (1.0 + min(0, pan))

        self.channel.set_volume(left, right)
