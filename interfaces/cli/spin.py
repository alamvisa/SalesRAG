import sys
import time
import threading

class Spinner:
    FRAMES = ['|', '/', '—', '\\']
    
    def __init__(self):
        self._thread = None
        self._running = False
        self._message = ""
    
    def _spin(self):
        i = 0
        while self._running:
            frame = self.FRAMES[i % len(self.FRAMES)]
            line = f'{frame} {self._message}'
            sys.stdout.write(f'\r{line:<50}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    
    def start(self, message: str):
        sys.stdout.write('\r' + ' ' * 40 + '\r')
        sys.stdout.flush()
        self._message = message
        self._running = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()
    
    def update(self, message: str):
        self._message = message
    
    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
        sys.stdout.flush()