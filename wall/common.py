"""
All commons are here
"""
from dataclasses import dataclass


@dataclass
class Common:
    """
    Define constants
    """
    BLACK = (0, 0, 0)
    BALL_IMAGE_NAME = 'ColorfulBall.png'
    PING_IMAGE_NAME = 'BarPingPong.png'
    BRICK_IMAGE_NAME = 'PsycheBrick.png'
    UNBREAKABLE_BRICK_IMAGE_NAME = 'IceBrick.png'
    POISONED_BRICK_IMAGE_NAME = 'PoisonedBrick.png'
