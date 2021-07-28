from constants import *
import pygame
import textwrap


class Message:
    def __init__(self, text, color):
        self.plain_text = text
        self.color = color
        self.count = 1

    @property
    def full_text(self):
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    def __init__(self):
        self.small_font = pygame.font.SysFont('arial', 12)
        self.messages = []

    def add_message(self, text, color, stackable):
        if stackable and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, color))

    def render(self, surface, x, y, width, height):
        y_offset = 0
        for message in reversed(self.messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                label = self.small_font.render(line, True, message.color)
                surface.blit(label, (x, y+y_offset))
                y_offset += 12
                if y_offset > height:
                    return
