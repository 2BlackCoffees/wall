"""
Handles the score
"""
from typing import Tuple
import pygame
from wall.static_sprite import Display

class Score(pygame.sprite.Sprite):
    font: pygame.font = None
    score: int = 0
    red: Tuple[int, int, int] = (255, 0, 0)
    black: Tuple[int, int, int] = (0, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)
    display: Display = None
    height = 0

    def __init__(self, screen: pygame.Surface, height: int):
        super().__init__()
        pygame.font.init()
        self.font:  pygame.Font = pygame.font.SysFont('Comic Sans MS', 30)
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.display = Display(screen, screen_width, screen_height)
        self.height = height

    def add_score(self, added_score) -> None:
        self.score += added_score

    def get_score_images(self):
        color_score: Tuple[int, int, int] = self.green
        if self.score < 0:
            color_score = self.red

        text_surface = self.font.render('Your score: ', False, self.blue)
        score_surface =  self.font.render(str(self.score), False, color_score)
        return text_surface, score_surface

    def display_on_screen(self) -> None:
        text_surface: pygame.Surface = None
        score_surface: pygame.Surface = None

        text_surface, score_surface = self.get_score_images()
        whole_width: int = text_surface.get_width() + score_surface.get_width()
        left_pos_text: int = (self.display.screen_width - whole_width ) // 2
        left_pos_score = left_pos_text + text_surface.get_width()
        top_pos = (self.height // 2 - max(text_surface.get_height(), score_surface.get_height())) 
        
        self.display.screen.blit(text_surface, (left_pos_text, top_pos))
        self.display.screen.blit(score_surface, (left_pos_score, top_pos))


    
