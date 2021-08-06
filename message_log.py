from constants import *


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
        self.messages = []

    def add_message(self, text, color, stackable):
        if stackable and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, color))
