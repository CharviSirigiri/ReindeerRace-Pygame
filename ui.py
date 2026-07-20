import pygame
from settings import screen, OUTLINE_COLOR

def draw_text(text, font_obj, text_col, x, y, outline_col=None):
    outline_col = outline_col or OUTLINE_COLOR
    base = font_obj.render(text, True, text_col)
    outline = font_obj.render(text, True, outline_col)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        screen.blit(outline, (x + dx, y + dy))
    screen.blit(base, (x, y))

def draw_text_to_surface(surface, text, font_obj, text_col, x, y, outline_col=None):
    outline_col = outline_col or OUTLINE_COLOR
    base = font_obj.render(text, True, text_col)
    outline = font_obj.render(text, True, outline_col)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, (x, y))

def draw_panel(surface, rect, fill_color, border_radius=12, border_color=None):
    """Draw a rounded panel with optional border."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill_color, (0, 0, rect.width, rect.height), border_radius=border_radius)
    if border_color:
        pygame.draw.rect(panel, border_color, (0, 0, rect.width, rect.height), 2, border_radius=border_radius)
    surface.blit(panel, rect.topleft)

class Button:
    def __init__(self, x, y, image):
        self.base_image = image
        self.rect = self.base_image.get_rect(topleft=(x, y))
        self.clicked = False
        self.press_timer = 0

    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    def draw(self, surface=None):
        action = False
        pos = pygame.mouse.get_pos()
        surf = surface or screen

        hover = self.rect.collidepoint(pos)
        pressed = pygame.mouse.get_pressed()[0] == 1

        if hover and pressed and not self.clicked:
            self.clicked = True
            action = True
            self.press_timer = 5

        if not pressed:
            self.clicked = False

        scale = 0.94 if self.press_timer > 0 else (1.06 if hover else 1.0)
        if self.press_timer > 0:
            self.press_timer -= 1

        if scale != 1.0:
            w, h = self.base_image.get_size()
            img = pygame.transform.smoothscale(self.base_image, (int(w * scale), int(h * scale)))
            draw_rect = img.get_rect(center=self.rect.center)
            surf.blit(img, draw_rect)
        else:
            surf.blit(self.base_image, self.rect)
        return action
