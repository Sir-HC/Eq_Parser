#Threads.py
import time
from PySide6.QtCore import QThread, Slot
from Watchers import FileOnModifiedHandler, Watcher

DIRECTORY = 'C:\Program Files (x86)\EverQuest\Logs'

class Thread(QThread):
    """
    Worker thread
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        """
        Initialize the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        try:
            print("start of thread")
            # watch directory
            result = self.fn(*self.args, **self.kwargs)

            print("end of thread", result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]

class File_Stream_Thread(Thread):

    def __init__(self, current_file, signals, *args, **kwargs):
        super().__init__(self.log_lines, *args, **kwargs)
        self.current_file = current_file
        self.directory = DIRECTORY
        self.signals = signals

    def log_lines(self):
        self.logfile = open(self.directory + '\\' + self.current_file, 'r')
        loglines = self.logtail(self.logfile)

        for line in loglines:
            self.signals.result.emit(line)

    def logtail(self, logfile):
        thefile = logfile
        thefile.seek(0, 2)
        while True:
            line = thefile.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line
			
			
class Watch_Directory_Thread(Thread):

    def __init__(self, directory, signals=None, *args, **kwargs):
        if not signals:
            raise ValueError('signals must be passed')
        super().__init__(self.watch_directory, signals=signals, *args, **kwargs)
        self.directory = directory

    def watch_directory(self, signals=None):
        self.watcher = Watcher(FileOnModifiedHandler(signals), self.directory)
        print(f"start watch on {self.directory}")
        res = self.watcher.run()
        print("watcher stoped")
        return res
		

