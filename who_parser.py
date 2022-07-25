import sys
import time
import traceback
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget
from Threads import File_Stream_Thread, Watch_Directory_Thread

DIRECTORY = 'C:\Program Files (x86)\EverQuest\Logs'


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.directory = DIRECTORY
        self.file = None
        self.watch_directory_signals = WorkerSignals()
        self.watch_directory_signals.result.connect(self.file_compare)
        self.watch_directory_thread = Watch_Directory_Thread(
            self.directory, signals=self.watch_directory_signals)
        self.watch_directory_thread.start()
        
        self.file_stream_thread = None 
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

    def file_compare(self, file):
        if self.file != file:
            self.file = file
            self.start_file_stream(self.file)

    def file_compare_new(self, file):
        if self.file is None:
            #first start up of start_file_stream
            self.start_file_stream(self.file)
        if self.file != file:
            old_file = self.file
            new_file = file
            self.switch_file_stream(old_file, new_file)

    def set_text(self, line):
        new_line = line
        current_text = self.editor.toPlainText()
        updated_text = current_text + new_line
        self.editor.setPlainText(updated_text)

    def start_file_stream(self, new_file):
        self.file = new_file
        self.file_stream_signals = WorkerSignals()
        self.file_stream_signals.result.connect(self.set_text)
        self.file_stream_thread = File_Stream_Thread(
            self.file, self.file_stream_signals)
        self.file_stream_thread.start()

    def closeEvent(self, event):
        # events to trigger when app is closed out
        self.directory_watch_thread.terminate()
        self.file_stream_thread.terminate()

    def clear_text(self):
        self.editor.setPlainText("")
        self.start_file_stream()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
