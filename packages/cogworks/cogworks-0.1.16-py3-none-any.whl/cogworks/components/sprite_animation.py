import os

from dataclasses import dataclass, field
from typing import Callable

from cogworks import Component
from cogworks.components.sprite import Sprite
from cogworks.exceptions import MissingComponentError


@dataclass
class Animation:
    name: str
    sprite_path: str
    start_sprite_index: int = 1
    last_sprite_index: int = 1
    time_between_sprites: float = 0.1
    # key = sprite index, value = list of callbacks
    events: dict[int, list[Callable]] = field(default_factory=dict)

    def add_event(self, index: int, callback: Callable):
        """Attach a callback to be fired when the animation reaches a specific frame index."""
        if index not in self.events:
            self.events[index] = []
        self.events[index].append(callback)

    def trigger_events(self, index: int):
        """Trigger all callbacks registered for a specific index."""
        for callback in self.events.get(index, []):
            callback()


class SpriteAnimation(Component):

    def __init__(self):
        super().__init__()

        self.animations: list[Animation] = []
        self.selected_animation: Animation | None = None

        self.sprite_index = 0
        self.animation_timer = 0.0
        self.sprite: Sprite | None = None

    def start(self):
        self.sprite_index = 0
        self.animation_timer = 0.0

        self.sprite = self.game_object.get_component(Sprite)
        if self.sprite is None:
            raise MissingComponentError(Sprite, self.game_object)

    def update(self, dt: float):
        if self.selected_animation is None or self.sprite is None:
            return

        self.animation_timer += dt

        if self.animation_timer >= self.selected_animation.time_between_sprites:
            path = self.selected_animation.sprite_path

            base, ext = os.path.splitext(path)
            new_path = f"{base}{self.sprite_index}{ext}"
            self.sprite.change_image(new_path)

            # Trigger events for this frame
            self.selected_animation.trigger_events(self.sprite_index)

            self.sprite_index += 1
            if self.sprite_index > self.selected_animation.last_sprite_index:
                self.sprite_index = self.selected_animation.start_sprite_index

            self.animation_timer = 0.0

    def clear_selected_animation(self):
        """Clears the selected animation so that none will play."""
        self.selected_animation = None

    def set_animation(self, name: str):
        """Change the selected animation."""
        self.selected_animation = next(
            (anim for anim in self.animations if anim.name == name), None
        )

        if self.selected_animation is None:
            print(f"[WARNING] Animation '{name}' not found.")
            return

        self.sprite_index = self.selected_animation.start_sprite_index

    def add_animation(
        self,
        name: str,
        sprite_path: str,
        start_sprite_index: int = 1,
        last_sprite_index: int = 1,
        time_between_sprites: float = 0.1,
    ):
        """ Add a sprite animation. The path to the sprite shouldn't include an index, for example use: "/goblin.png" and the system will generate "/goblin_0.png", "/goblin_1.png", etc. """
        if time_between_sprites < 0.1:
            print("[WARNING] The time_between_sprites should be at least 0.1.")
            time_between_sprites = 0.1

        animation = Animation(
            name=name,
            sprite_path=sprite_path,
            start_sprite_index=start_sprite_index,
            last_sprite_index=last_sprite_index,
            time_between_sprites=time_between_sprites,
        )

        self.animations.append(animation)
        return animation
