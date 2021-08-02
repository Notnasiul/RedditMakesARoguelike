import pygame


def render_bar(engine, surface, x, y, value, max_value, text, width, height, border, bkg_color, fg_color, txt_color):
    pygame.draw.rect(surface, bkg_color, pygame.Rect(x, y, width, height))
    pygame.draw.rect(surface, fg_color, pygame.Rect(
        x+border, y+border,
        width * (value/max_value) - border*2, height-border*2))

    label = engine.small_font.render(
        f"{text}: {value}/{max_value}", True, txt_color)
    surface.blit(label, (x+border*2, y + height/2 - 3))
