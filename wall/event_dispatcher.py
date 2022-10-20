"""
Event dispatcher
"""
import pygame
from wall.sprites import GameMovingSprite

class EventDispatcher():
    """
    Event dispatcher informs registered sprites when specific events occur like
    mouse move or key pressed
    """
    is_done_status: bool = False
    controlled_moving_sprites: list = []

    def subscribe(self, controlled_moving_sprite: GameMovingSprite) -> None:
        """
        Attach a new sprite
        """
        self.controlled_moving_sprites.append(controlled_moving_sprite)

    def unsubscribe(self, controlled_moving_sprite: GameMovingSprite) -> None:
        """
        Detach a sprite
        """
        self.controlled_moving_sprites.remove(controlled_moving_sprite)

    def is_done(self) -> bool:
        """
        Inform if is done is required
        """
        return self.is_done_status

    def process_event(self) -> None:
        """
        Handle the events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_done_status = True

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.is_done_status = True

                for controlled_moving_sprite in self.controlled_moving_sprites:
                    controlled_moving_sprite.start_direction(event.key)

            if event.type == pygame.KEYUP:
                for controlled_moving_sprite in self.controlled_moving_sprites:
                    controlled_moving_sprite.stop_direction(event.key)

            if event.type == pygame.MOUSEMOTION:
                for controlled_moving_sprite in self.controlled_moving_sprites:
                    controlled_moving_sprite.mouse_position_move(pygame.mouse.get_pos())
