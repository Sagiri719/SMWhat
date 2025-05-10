import tkinter as tk
from tkinter import font as tkfont
import time;

class MarqueeLabel:
    def __init__(self, master, text: tk.StringVar, font, width=30, speed=150, bg="white"):
        
        self.master = master;
        self.base_text = text.get();

        self.display_text = text;
        self.width_chars = width;

        self.show_text = tk.StringVar(master, self.base_text);

        self.font = tkfont.Font(font=font);
        self.label = tk.Label(master, textvariable=self.show_text, font=font, justify=tk.CENTER, width=width, anchor='center', bg=bg)
        self.label.pack(pady=5, fill=tk.X);

        self.label_width = self.label.winfo_width();

        
        self.pos = 0;
        self.speed = speed;
        self.should_scroll = False;

        self.label.after(100, self.scroll);
        text.trace("w", self.update_text);

    def update_text(self, *args, **kwargs):
        self.base_text = self.display_text.get() + " " * 10

        text_width = self.font.measure(self.base_text)
        self.should_scroll = text_width > self.label.winfo_width()

        # When not scrolling, show the centered text statically
        if not self.should_scroll:
            padded = self.display_text.get().center(self.width_chars)
            self.show_text.set(padded)

    fps = 60;
    last_frame = 0;

    def scroll(self):

        if self.last_frame > 0:
            delta_time = time.time() - self.last_frame;
            self.fps = 1 / delta_time;

        if self.should_scroll:

            self.pos += 1
            if self.pos >= len(self.base_text):
                self.pos = 0

            # Double the text so we can take a full slice even if wrapping
            doubled_text = self.base_text + self.base_text
            new_text = doubled_text[self.pos:self.pos + self.width_chars]

            self.show_text.set(new_text)

        self.last_frame = time.time();
        self.master.after(int(10000 / self.speed), self.scroll);
        