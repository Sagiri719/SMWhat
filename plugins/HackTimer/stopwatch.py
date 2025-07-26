import time;

class Stopwatch:
    def __init__(self):
        self.reset();

    def start(self):
        if not self.running:
            self.start_time = time.time();
            self.running = True;

    def stop(self):
        self.reset();

    def reset(self):
        self.start_time = None;
        self.elapsed_time = 0;
        self.running = False;

    def pause(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time;
            self.running = False;

    def resume(self):
        self.start();

    def set_time(self, seconds: float):
        self.elapsed_time = seconds;
        if self.running:
            self.start_time = time.time();

    def elapsed(self):
        if self.running:
            return self.elapsed_time + (time.time() - self.start_time);
        
        return self.elapsed_time;