import pygame
from cogworks.component import Component
from cogworks.components.transform import Transform
from cogworks.components.rigidbody2d import Rigidbody2D
from cogworks.utils.asset_loader import load_user_image


class Sprite(Component):
    def __init__(
        self,
        image_path: str,
        offset_x: float = 0,
        offset_y: float = 0,
        scale_factor: float = 1.0,
        alpha: int = 255,
        flip_x: bool = False,
        flip_y: bool = False,
        pixel_art_mode: bool = False
    ):
        """
        Sprite component to render an image associated with a GameObject.

        Args:
            image_path (str): Path to the image file (inside 'assets' folder).
            offset_x (float): Offset on the x-axis of the sprite relative to the Transform
            offset_y (float): Offset on the y-axis of the sprite relative to the Transform
            scale_factor (float): Scale multiplier of the sprite image
            alpha (int): Transparency of the sprite image (0-255)
            flip_x (bool): Flip the sprite image on the x-axis
            flip_y (bool): Flip the sprite image on the y-axis
            pixel_art_mode (bool): If True, disables smooth scaling for crisp pixel art (default: False)
        """
        super().__init__()
        self.image_path = image_path
        self.original_image = load_user_image(image_path).convert_alpha()
        self.image = self.original_image  # Current transformed image
        self.rect = self.image.get_rect()  # Rect for positioning and collision
        self.transform: Transform = None
        self._last_transform_state = None  # Cache to detect Transform changes
        self.camera = None
        self._scaled_image_cache = {}  # Cache for scaled images (scale, zoom) -> pygame.Surface
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale_factor = scale_factor
        self.alpha = alpha  # Store alpha value
        self.flip_x = flip_x  # Flip horizontally
        self.flip_y = flip_y  # Flip vertically
        self.pixel_art_mode = pixel_art_mode

    def start(self):
        self.transform = self.game_object.get_component(Transform)
        self.camera = self.game_object.scene.camera_component
        if not self.transform:
            self.transform = Transform()
            self.game_object.add_component(self.transform)

        # Box rigidbody config
        rb: Rigidbody2D = self.game_object.get_component(Rigidbody2D)
        if rb and (rb.width == 0 or rb.height == 0):
            # Use unscaled image size for collider
            rb.width = self.original_image.get_width()
            rb.height = self.original_image.get_height()

        # Apply the transform once on start
        self._apply_transform()

    def _apply_transform(self):
        """
        Internal: rebuild the sprite image if scale/rotation changed
        """
        sx, sy = self.transform.get_local_scale()
        angle = self.transform.local_rotation

        sx *= self.scale_factor
        sy *= self.scale_factor

        avg_scale = (sx + sy) / 2 if (sx != sy) else sx

        if self.pixel_art_mode:
            w = int(self.original_image.get_width() * sx)
            h = int(self.original_image.get_height() * sy)
            scaled_image = pygame.transform.scale(self.original_image, (w, h))
            if angle != 0:
                scaled_image = pygame.transform.rotate(scaled_image, angle)
            self.image = scaled_image
        else:
            self.image = pygame.transform.rotozoom(self.original_image, angle, avg_scale)

        if self.flip_x or self.flip_y:
            self.image = pygame.transform.flip(self.image, self.flip_x, self.flip_y)

        self.image.set_alpha(self.alpha)

        final_x = self.transform.local_x + self.offset_x * self.scale_factor
        final_y = self.transform.local_y + self.offset_y * self.scale_factor

        self.rect = self.image.get_rect(center=(final_x, final_y))
        self._last_transform_state = (sx, sy, self.transform.local_rotation, self.flip_x, self.flip_y, self.pixel_art_mode)
        self._scaled_image_cache.clear()

    def update(self, dt: float):
        if not self.transform:
            return

        sx, sy = self.transform.get_local_scale()
        state = (sx, sy, self.transform.local_rotation, self.flip_x, self.flip_y, self.pixel_art_mode)

        if state != self._last_transform_state:
            self._apply_transform()

    def render(self, surface):
        if not self.transform or not self.image:
            return

        x, y = self.transform.get_world_position()
        x += self.offset_x * self.scale_factor
        y += self.offset_y * self.scale_factor

        img = self.image
        w, h = img.get_size()

        zoom = self.camera.zoom if self.camera else 1.0
        cache_key = (w, h, zoom, self.scale_factor, self.alpha, self.flip_x, self.flip_y, self.pixel_art_mode)
        if cache_key in self._scaled_image_cache:
            img_scaled = self._scaled_image_cache[cache_key]
            w_scaled, h_scaled = img_scaled.get_size()
        else:
            w_scaled, h_scaled = int(w * zoom), int(h * zoom)
            if self.pixel_art_mode:
                img_scaled = pygame.transform.scale(img, (w_scaled, h_scaled))
            else:
                img_scaled = pygame.transform.smoothscale(img, (w_scaled, h_scaled))
            img_scaled.set_alpha(self.alpha)
            self._scaled_image_cache[cache_key] = img_scaled

        if self.camera and not self.camera.is_visible(x=x, y=y, width=w_scaled, height=h_scaled):
            return

        if self.camera:
            screen_x, screen_y = self.camera.world_to_screen(x, y)
            surface.blit(img_scaled, (screen_x - w_scaled // 2, screen_y - h_scaled // 2))
        else:
            rect = img_scaled.get_rect(center=(x, y))
            surface.blit(img_scaled, rect.topleft)

    def change_image(self, new_image_path: str):
        """
        Change the sprite image at runtime.

        Args:
            new_image_path (str): Path to the new image file.
        """
        self.image_path = new_image_path
        self.original_image = load_user_image(new_image_path).convert_alpha()
        self._apply_transform()  # Immediately apply to match current transform

    def set_alpha(self, alpha: int):
        """
        Set sprite transparency at runtime.

        Args:
            alpha (int): 0 = fully transparent, 255 = fully opaque
        """
        self.alpha = max(0, min(255, alpha))
        if self.image:
            self.image.set_alpha(self.alpha)
        self._scaled_image_cache.clear()

    def get_width(self) -> float:
        """
        Returns:
            float: The scaled width of the sprite image.
        """
        return self.image.get_width()

    def get_height(self) -> float:
        """
        Returns:
            float: The scaled height of the sprite image.
        """
        return self.image.get_height()

    def _get_scale(self, transform: 'Transform', axis: str) -> float:
        """
        Internal helper to get the scaling factor for a given axis ('x' or 'y').

        Args:
            transform (Transform): Optional transform provided by the caller.
            axis (str): Either 'x' or 'y' to indicate which scale to return.

        Raises:
            ReferenceError: If no transform is provided and the sprite has no own transform.

        Returns:
            float: The scale factor along the specified axis.
        """
        if transform is None:
            if self.transform is None:
                raise ReferenceError(
                    "Sprite doesn't have reference to Transform yet. Provide one or call this method in start()/update()."
                )
            transform = self.transform

        if axis == 'x':
            return transform.local_scale_x
        elif axis == 'y':
            return transform.local_scale_y
        else:
            raise ValueError("Axis must be 'x' or 'y'.")
