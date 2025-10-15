import logging
import time
import threading

class TimeMonitorAgent:
    def __init__(self, max_duration, notify_callable, count = 0):
        self.max_duration = max_duration
        self.notify_callable = notify_callable
        self._stop_event = threading.Event()
        self.thread = None
        self.count = count

    def start(self):
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self._stop_event.clear()
        self.thread.start()

    def restart(self):
        self.start_time = time.time()
        self._stop_event.clear()
        
    def _run(self):
        while not self._stop_event.is_set():
            time.sleep(1)
            elapsed_time = time.time() - self.start_time
            logging.info(elapsed_time)
            if elapsed_time >= self.max_duration:
               self.count = self.count + 1
               self._stop_event.set()
               self.notify_callable(self.count)    
        return

    def stop(self):
        self._stop_event.set()
        