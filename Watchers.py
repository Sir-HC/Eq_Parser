from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class Watcher:

    def __init__(self, response_function, directory):
        self.observer = Observer()
        self.response_function = response_function
        self.directory = directory

    def run(self):
        self.observer.schedule(self.response_function,
                               self.directory, recursive=False)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)

        except:
            self.observer.stop()
            self.observer.join()
            return 0
        return 1

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            return 1
        return 0
        
class FileOnModifiedHandler(FileSystemEventHandler):

    def __init__(self, signals):
        self.signals = signals
        self.last_emit = 0

    def on_modified(self, event):
        
        self.file_name = event.src_path.split('\\')[-1]
        # print(f'file modified: {self.file_name}')
        if self.signals and self.file_name != 'dbg.txt':
            if (time.time() - self.last_emit) > 5:
                self.signals.result.emit(self.file_name)
                self.last_emit = time.time()
            # print(f'emitting file modified: {self.file_name}')