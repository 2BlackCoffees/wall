"""
Handle all sprites
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
import pygame
from wall.collision_handler import CollisionHandler
from wall.static_sprite import StaticSprite

class GameMovingSprite(StaticSprite, ABC):
    """
    Moving sprites should inherit me and provide their own functionality
    """

    change_x = 0
    change_y = 0

    def change_speed(self, horizontal_speed: int, vertical_speed: int) -> None:
        """
        Increase / decrease speed (decrease with negative values)
        """
        self.change_x += horizontal_speed
        self.change_y += vertical_speed

    def set_change_speed_x(self, horizontal_speed: int) -> None:
        """
        Set new horizontal speed
        """
        self.change_x = horizontal_speed

    def set_change_speed_y(self, vertical_speed: int) -> None:
        """
        Set new vertical speed
        """
        self.change_y = vertical_speed

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Analyze collision taking into account next position
        """
        return (self.image.rect.x + self.change_x,
                self.image.rect.y + self.change_y)

    def change_speed_factor(self, factor_x: int, factor_y: int) -> None:
        """
        Speed factor should not be greater than half of the size of the sprite
        otherwise movement will not be fluid anymore
        """
        if abs(self.change_x) < self.image.width / 2:
            self.change_x *= factor_x
        if abs(self.change_y) < self.image.height / 2:
            self.change_y *= factor_y

    def move(self) -> None:
        """
        Default move
        """
        self.image.rect.x += self.change_x
        self.image.rect.y += self.change_y



class UserControlledGameMovingSprite(GameMovingSprite, ABC):
    """
    This is purely user controlled class
    """

    @abstractmethod
    def start_direction(self, direction: int) -> None:
        """
        Start moving in the specified direction
        """

    @abstractmethod
    def stop_direction(self, direction: int) -> None:
        """
        Stop moving
        """

    @abstractmethod
    def mouse_position_move(self, mouse_position: Tuple[int, int]) -> None:
        """
        Provide mous coordinates
        """


class Ball(GameMovingSprite):
    """
    This is the sprite representing the ball bumping
    """
    horizontal: int = CollisionHandler.HORIZONTAL
    vertical: int = CollisionHandler.VERTICAL
    left: int = CollisionHandler.LEFT
    right: int = CollisionHandler.RIGHT
    top: int = CollisionHandler.TOP
    bottom: int = CollisionHandler.BOTTOM
    horizontal_collision: bool = False
    vertical_collision: bool = False
    def __init__(self, screen: pygame.Surface):

        super().__init__(screen)
        self.change_x: int = 5
        self.change_y: int = 5

    def bumped(self, from_side_bumped: dict) -> None:

        self.horizontal_collision, _ = \
            self.collision_handler.horizontal_collision_side_bumped(from_side_bumped)

        self.vertical_collision, _ = \
            self.collision_handler.vertical_collision_side_bumped(from_side_bumped)

    def move(self) -> None:
        if self.collision_handler is not None:
            self.collision_handler.inform_sprite_about_to_move()

        if self.horizontal_collision or \
           (self.image.rect.x < 1 or \
            self.image.rect.x + self.image.width > self.display.screen_width):
            self.change_x = -self.change_x



        if self.vertical_collision or \
           (self.image.rect.y < 1 or \
            self.image.rect.y + self.image.height > self.display.screen_height):
            self.change_y = -self.change_y
            if self.image.rect.y + self.image.height > self.display.screen_height:
                self.collision_handler.add_score(-500) 

        self.horizontal_collision = False
        self.vertical_collision = False

        self.change_speed_factor(1.05, 1.05)
        super().move()

class BreakableBrick(StaticSprite):
    number_remaining_bumps = 5

    def bumped(self, from_side_bumped: dict) -> None:
        if self.number_remaining_bumps > 0:
            self.collision_handler.add_score(5)
            self.number_remaining_bumps -= 1
        elif self.collision_handler == 0:
            self.collision_handler.add_score(100)

    def display_on_screen(self) -> None:
        if self.number_remaining_bumps == 0:
            self.collision_handler.unsubscribe(self)    
            self.number_remaining_bumps -= 1    
        if self.number_remaining_bumps > 0:
            super().display_on_screen()

class UnbreakableBrick(StaticSprite):
    def bumped(self, from_side_bumped: dict) -> None:
        pass

class PoisonedBrick(StaticSprite):
    def bumped(self, from_side_bumped: dict) -> None:
        self.collision_handler.add_score(-10)


class Player(UserControlledGameMovingSprite):
    """
    This is the concrete user player class
    """
    next_position_x: int = 0

    def set_position(self, pos_x: int, pos_y: int) -> StaticSprite:
        """
        Set new position of user with coordinates
        """
        super().set_position(pos_x, self.display.screen_height - self.image.height)
        self.next_position_x = pos_x
        return self

    def start_direction(self, direction: int) -> None:
        """
        This starts movement with the keyboard
        """
        if direction == pygame.K_LEFT:
            self.change_speed(-5, 0)
        if direction == pygame.K_RIGHT:
            self.change_speed(5, 0)
        if direction == pygame.K_UP:
            self.change_speed(0, -5)
        if direction == pygame.K_DOWN:
            self.change_speed(0, 5)

    def stop_direction(self, direction) -> None:
        """
        This stops movement with the keyboard
        """
        if direction in (pygame.K_LEFT, pygame.K_RIGHT):
            self.set_change_speed_x(0)
        if direction in (pygame.K_UP, pygame.K_DOWN):
            self.set_change_speed_y(0)

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
        return (self.next_position_x, self.image.rect.y)

    def mouse_position_move(self, mouse_position) -> None:
        """
        This moves with the mouse
        """
        self.change_x = 0
        self.change_y = 0
        mouse_position_x, _ = mouse_position
        if self.image.width // 2 < \
           mouse_position_x < self.display.screen_width - self.image.width // 2:
            self.next_position_x = mouse_position_x -  self.image.width // 2
            if self.collision_handler is not None:
                self.collision_handler.inform_sprite_about_to_move()
            self.image.rect.x = self.next_position_x
        #if(mouse_position_y > self.height // 2 and
        # mouse_position_y < self.screen_height - self.height // 2):
        #    self.rect.y = mouse_position_y -  self.height // 2

    def bumped(self, from_side_bumped: dict) -> None:
        horizontal_collision, _ = \
            self.collision_handler.horizontal_collision_side_bumped(from_side_bumped)
        if horizontal_collision:
            self.collision_handler.add_score(1)

    def move(self) -> None:
        """
        TODO: This must be removed
        """
        super().change_speed_factor(1.10, 1.10)
        if(self.image.rect.x + self.change_x < 1 or \
           self.image.rect.x + self.image.width + self.change_x > \
           self.display.screen_width):
            self.change_x = 0
        #if(self.rect.y + self.change_y < 1 or
        # self.rect.y + self.height + self.change_y > self.screen_height):
        #    self.change_y = 0

        super().move()
