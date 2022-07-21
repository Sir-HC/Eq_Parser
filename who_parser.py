import sys
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import QThread, Slot, Signal, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget


DIRECTORY = 'C:\\Program Files (x86)\\EverQuest\\Logs'


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class Watcher:

    def __init__(self, response_function, directory):
        self.observer = Observer()
        self.response_function = response_function
        self.directory = directory
        
    def run(self):
        self.observer.schedule(self.response_function, self.directory, recursive=False)
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
            #watch directory
            result = self.fn(*self.args, **self.kwargs)
            
            print("end of thread", result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]

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
            
            
class FileOnModifiedHandler(FileSystemEventHandler):

    def __init__(self, signals):
        self.signals = signals
    
    def on_modified(self, event):
        self.file_name = event.src_path.split('\\')[-1]
        print(f'file modified: {self.file_name}, ', end='')
        if self.signals and self.file_name != 'dbg.txt':
            self.signals.result.emit(self.file_name)
            print(f'emitting file modified: {self.file_name}')
        


            


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        
        self.directory = DIRECTORY
        self.signals = WorkerSignals()
        self.signals.result.connect(self.set_text)
        self.directory_watch_thread = Watch_Directory_Thread(self.directory, signals=self.signals)
        self.directory_watch_thread.start()



        self.setWindowTitle("Who Parser")

        widget = QWidget()
        layout = QVBoxLayout()
        
        self.editor = QPlainTextEdit()
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)

        layout.addWidget(self.editor)
        layout.addWidget(self.clear_button)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()


    def set_text(self, current_file):
        print(f"in set_text: {current_file}")
        # textbox = self.editor.toPlainText()
        # if textbox == "":
        #     self.logfile = open(self.log_file, "r")
        #     loglines = self.log_tail(self.logfile)
        #     for line in loglines:
        #         print(line)

    def closeEvent(self, event):
        # events to trigger when app is closed out
        self.directory_watch_thread.terminate()

    def clear_text(self):
        self.editor.setPlainText("")
        self.set_text()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())


# def worker_output(self, s):
#     self.editor.setPlainText(s)

# def worker_error(self, t):
#     print("ERROR: %s" % t)

# def log_tail(self, current_file):
#     print("log_tail has been called")
#     file_to_follow = current_file
#     file_to_follow.seek(0, 2)
#     while True:
#         line = file_to_follow.readline()
#         if not line:
#             time.sleep(0.1)
#             continue
#         yield line

# def search_who():

#     who = []
#     match = "players in"
#     top_of_search = "Players on EverQuest:"
#     end = True
#     y = -1

#     with open(latest_file, encoding='ISO-8859-1') as f:
#         lines = f.readlines()
#         last_line = lines[-1]

#         if match in last_line:
#             while end:
#                 if top_of_search in lines[y]:
#                     end = False
#                 who.insert(0, lines[y].strip())
#                 y -= 1
#             return who

# while go:
#                 results = search_who()
#                 if results != None:
#                     go = False
#                 if self.is_killed:
#                     raise WorkerKilledException
#             f = ""
#             for i in results:
#                 f += i + "\n"
