"""
Handle static sprites
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from dataclasses import dataclass
import pygame
from wall.collision_handler import CollisionHandler

@dataclass
class Display:
    """
    This data class factors all display related variables
    """
    screen: pygame.Surface = None
    screen_width: int = 0
    screen_height: int = 0

@dataclass
class Image:
    """
    This data class factors all images related variables
    """
    image: pygame.Surface = None
    width: int = 0
    height: int = 0
    perimeter: list(dict) = None
    rect: pygame.Rect = None


class StaticSprite(pygame.sprite.Sprite, ABC):
    """
    Static sprites cannot move, moving sprites are handled by another class
    TODO: A build in the builder patter is needed
    """
    collision_handler: CollisionHandler = None
    display: Display = None
    image: Image = None

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.display = Display(screen, screen_width, screen_height)

    def set_collision_handler(self, collision_handler: CollisionHandler) -> StaticSprite:
        """
        Attach a collision handler
        """
        self.collision_handler = collision_handler
        return self

    def set_position(self, pos_x: int, pos_y: int) -> StaticSprite:
        """
        Define position of the sprite
        """
        if self.image is not None and self.image.rect is not None:
            self.image.rect.x = pos_x - self.image.width // 2
            self.image.rect.y = pos_y - self.image.height // 2
        else:
            print("Error trying to set a position on an image "
                  "that does not exist yet! Set the image first!")
        return self

    def set_image(self, width: int, height: int,
                  image_path: str) -> StaticSprite:
        """
        Define the position of the sprite
        """
        if self.image is not None and self.image.rect is not None:
            self.image.rect.x += self.image.width // 2
            self.image.rect.y += self.image.height // 2

        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        perimeter = [{'x': 0, 'y': 0}, {'x': width, 'y': height}]
        self.image = Image(image, width, height, perimeter,
                           image.get_rect())

        self.set_position(self.image.rect.x, self.image.rect.y)

        return self

    def display_on_screen(self) -> None:
        """
        Paint the sprite on the screen
        """
        self.display.screen.blit(self.image.image, (self.image.rect.x,self.image.rect.y))

    def get_perimeter(self) -> list({}):
        """
        Get the perimeter of the sprite (Currently only as rectanle)
        """
        return self.image.perimeter

    def get_perimeter_optimized(self) -> list({}):
        """
        Get the surrounding rectangle for optimization
        """
        return self.image.perimeter

    def get_position(self) -> Tuple[int, int]:
        """
        Get the position of the sprite
        """
        return (self.image.rect.x, self.image.rect.y)

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
        return self.get_position()

    @abstractmethod
    def bumped(self, from_side_bumped: dict) -> None:
        """
        Inform that this sprite bumbed or was bumped
        """
