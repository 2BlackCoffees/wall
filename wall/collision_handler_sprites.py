"""
Handle collisions
"""
from typing import Tuple
#from pprint import pprint
from wall.collision_handler import CollisionHandler
from wall.static_sprite import StaticSprite
from wall.sprites import GameMovingSprite
from wall.score import Score

class CollisionHandlerSprites(CollisionHandler):
    """
    This class handles collisions:
    it checks whether 2 objects bumped against each other.
    """
    FROM_SIDE = 'from_side'
    SPRITE = 'sprite'
    PERIMETER='perimeter'
    PERIMETER_OPTIMIZED='perimeter_optimized'
    sprites: dict = {}
    dynamic_sprites: set = set()
    score = None

    def __init__(self, score: Score):
        self.score = score

    def subscribe_static(self, sprite: StaticSprite):
        """
        Subscribe a new static sprite which needs to be analyzed against a collision
        """
        self.sprites[sprite] = {self.PERIMETER:           sprite.get_perimeter(),
                                self.PERIMETER_OPTIMIZED: sprite.get_perimeter_optimized()}

    def subscribe_moving(self, sprite: GameMovingSprite):
        """
        Subscribe a new sprite which needs to be analyzed against a collision
        """
        self.dynamic_sprites.add(sprite)
        self.subscribe_static(sprite)

    def unsubscribe(self, sprite: StaticSprite):
        if sprite in self.sprites:
            del self.sprites[sprite]
        if sprite in self.dynamic_sprites:
            del self.dynamic_sprites[sprite]

    def __get_moved_perimeter_to_position(self,pos_x: int, pos_y: int,
                                          perimeter: list) -> list({}):
        return [{'x': pos_x + position['x'], 'y': pos_y + position['y']} \
                for position in perimeter]

    def __get_perimeter(self, sprite: StaticSprite, optimized: bool) -> list({}):
        """
        Get the proper perimeter
        """
        (pos_x, pos_y) = sprite.get_position_for_collision_analysis()
        key = self.PERIMETER_OPTIMIZED if optimized else self.PERIMETER
        return self.__get_moved_perimeter_to_position(pos_x, pos_y, self.sprites[sprite][key])

    def __points_collision(self, from_perimeter: list, perimeter: list) -> Tuple[bool, dict]:
        """
        Analyzes if a collision happened and which side collided
        """
        from_top_left_corner, from_bottom_right_corner = from_perimeter
        top_left_corner,      bottom_right_corner      = perimeter
        has_bumped: bool = False
        from_side_bumped: dict = {}

        if not (from_top_left_corner['x']     > bottom_right_corner['x'] or \
                from_bottom_right_corner['x'] < top_left_corner['x'] or \
                from_top_left_corner['y']     > bottom_right_corner['y'] or \
                from_bottom_right_corner['y'] < top_left_corner['y']):
            has_bumped = True
            from_diff_left   = bottom_right_corner['x']      - from_top_left_corner['x']
            from_diff_right  = from_bottom_right_corner['x'] - top_left_corner['x']
            from_diff_top    = from_bottom_right_corner['y'] - top_left_corner['y']
            from_diff_bottom = bottom_right_corner['y']      - from_top_left_corner['y']
            diff_horizontal  = min(from_diff_left, from_diff_right)
            diff_vertical    = min(from_diff_top, from_diff_bottom)

            if diff_horizontal < diff_vertical:
                if from_diff_top < from_diff_bottom:
                    from_side_bumped[self.HORIZONTAL] = from_diff_top
                else:
                    from_side_bumped[self.HORIZONTAL] = -from_diff_bottom

            elif diff_horizontal > diff_vertical:
                if from_diff_left < from_diff_right:
                    from_side_bumped[self.VERTICAL] = from_diff_left
                else:
                    from_side_bumped[self.VERTICAL] = -from_diff_right

        return has_bumped, from_side_bumped

    def horizontal_collision_side_bumped(self, from_side_bumped: dict) -> Tuple[bool, int]:
        """
        Says whether a collision happened horizontally
        """
        if self.HORIZONTAL in from_side_bumped:
            return True, from_side_bumped[self.HORIZONTAL]
        return False, 0


    def vertical_collision_side_bumped(self, from_side_bumped: dict) -> Tuple[bool, int]:
        """
        Says whether a collision happened vertically
        """
        if self.VERTICAL in from_side_bumped:
            return True, from_side_bumped[self.VERTICAL]
        return False, 0

    def inform_sprite_about_to_move(self) -> None:
        """
        When a moving sprite is about to move he should call this method first
        before moving: this will call the method bumped of all moving sprites
        that collided
        """
        optimized_perimeter: bool = True
        moving_sprites_collided: list = {}
        from_sprite: GameMovingSprite = None
        from_sprite: StaticSprite = None
        for from_sprite in self.dynamic_sprites:
            from_perimeter = self.__get_perimeter(from_sprite, optimized_perimeter)
            for sprite in self.sprites:
                if sprite != from_sprite:
                    perimeter: list = self.__get_perimeter(sprite, optimized_perimeter)
                    has_bumped, from_side_bumped = \
                          self.__points_collision(from_perimeter, perimeter)
                    if has_bumped:
                        moving_sprites_collided[from_sprite] = from_side_bumped
                        sprite.bumped(from_side_bumped)

        for from_sprite, from_side_bumped in moving_sprites_collided.items():
            from_sprite.bumped(from_side_bumped)

    def add_score(self, add_score: int) -> None:
        self.score.add_score(add_score)