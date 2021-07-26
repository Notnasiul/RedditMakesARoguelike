import pygame


def render_bar(surface, x, y, value, max_value, text, width, height, border, bkg_color, fg_color, txt_color):
    pygame.draw.rect(surface, bkg_color, pygame.Rect(x, y, width, height))
    pygame.draw.rect(surface, fg_color, pygame.Rect(
        x+border, y+border,
        width * (value/max_value) - border*2, height-border*2))

    small_font = pygame.font.SysFont('arial', 12)
    label = small_font.render(
        f"{text}: {value}/{max_value}", True, txt_color)
    surface.blit(label, (x+border*2, y+border*2))
