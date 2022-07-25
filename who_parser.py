import sys
import time
import traceback
import configparser
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, QObject, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget
from QThreads import File_Stream_Thread, Watch_Directory_Thread, Chunk_File_Stream_Thread


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        config = configparser.ConfigParser()
        config.read('config.ini')
        if config['DEFAULT']['Directory']:
            self.directory = config['DEFAULT']['Directory']
        else:
            #need to make dialog pop up for this and settings to change directory
            #raise ValueError('config.ini not set')
            self.directory = 'H:\Everquest\Logs'
        
        
        self.watch_directory_signals = WorkerSignals()
        self.watch_directory_signals.result.connect(self.file_compare)
        self.watch_directory_thread = Watch_Directory_Thread(self.directory, 
                                                             signals=self.watch_directory_signals)
        self.watch_directory_thread.start()
        
        
        self.file = None
        #self.file_stream_type = File_Stream_Thread
        self.file_stream_type = Chunk_File_Stream_Thread
        self.file_stream_signals = WorkerSignals()
        self.file_stream_signals.result.connect(self.set_text_list)
        self.file_stream_thread = None 
        
        
        
        self.setWindowTitle("Who Parser")
        self.setWindowIcon(QIcon('icon.jpg'))

        widget = QWidget()
        layout = QVBoxLayout()

        self.editor = QPlainTextEdit()
        self.editor.setMinimumSize(QSize(800, 600))
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)

        layout.addWidget(self.editor)
        layout.addWidget(self.clear_button)
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        
        #button_action = QAction()
        
        menu = self.menuBar()
        setting_menu = menu.addMenu("Settings")
        #setting_menu.addAction(button_action)

        self.show()


    def file_compare(self, file):
        if self.file == file:
            return
        
        prev_file = self.file
        self.file = file 
        char_name = self.file.split('_')[1]
        self.setWindowTitle(f"Who Parser - {char_name}")
        
        if prev_file is not None:
            self.file_stream_thread.terminate()
            self.file_stream_thread.wait()
            print(f'Prev thread running? {self.file_stream_thread.isRunning()}')
            print('switching file')
        # We were not watching a file, but one has been identified for us
        print('starting file')
        self.file_stream_thread = self.file_stream_type(self.directory,
                                                 self.file, self.file_stream_signals)
        self.file_stream_thread.start()
    

    def set_text(self, line):
        new_line = line
        current_text = self.editor.toPlainText()
        updated_text = current_text + new_line
        self.editor.setPlainText(updated_text)

    def set_text_list(self, lines):
        for line in lines:
            new_line = line
            current_text = self.editor.toPlainText()
            updated_text = current_text + new_line
            self.editor.setPlainText(updated_text)

    def closeEvent(self, event):
        # events to trigger when app is closed out
        self.watch_directory_thread.terminate()
        self.file_stream_thread.terminate()

    def clear_text(self):
        self.editor.setPlainText("")
        self.start_file_stream()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
