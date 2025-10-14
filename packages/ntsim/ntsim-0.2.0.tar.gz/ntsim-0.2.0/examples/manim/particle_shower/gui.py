import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QCheckBox, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import h5py
import pandas as pd

class ManimApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manim Qt5 Integration")
        self.setGeometry(100, 100, 600, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.exp_button = QPushButton("Export H5")
        self.exp_button.clicked.connect(self.importData)
        self.layout.addWidget(self.exp_button)

        self.run_button = QPushButton("Run Manim")
        self.run_button.clicked.connect(self.run_manim)
        self.layout.addWidget(self.run_button)

        self.output_label = QTextEdit()
        self.layout.addWidget(self.output_label)

    def run_manim(self):
        checklist = [self.file_name]
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                checklist.append(checkbox.text())

        with open('conf.txt', 'w') as txt_file:
            txt_file.write(','.join(checklist))

        self.worker = ManimWorker()
        self.worker.progress_signal.connect(self.update_output_label)
        self.worker.start()

    def importData(self):
        file_dialog = QFileDialog()
        self.file_name, _ = file_dialog.getOpenFileName(self, "Select HDF5 File", "", "HDF5 Files (*.h5)")
        if self.file_name:
            with h5py.File(self.file_name, 'r') as f:
                keys = list(f.keys())
                for key in f.keys():
                    print(key)
            self.event_keys = [key for key in keys if key.startswith('event_')]
            self.checkboxes = []
            for key in self.event_keys:
                checkbox = QCheckBox(key)
                checkbox.setChecked(True)
                self.checkboxes.append(checkbox)
                self.layout.addWidget(checkbox)

    def update_output_label(self, text):
        self.output_label.append(text)

class ManimWorker(QThread):
    progress_signal = pyqtSignal(str)

    def run(self):
        try:
            # Run the Manim script using subprocess
            result = subprocess.Popen(["manimgl", "h5_shower.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            while True:
                line = result.stdout.readline()
                if not line:
                    break
                self.progress_signal.emit(line)
            result.stdout.close()
            result.wait()
        except Exception as e:
            self.progress_signal.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManimApp()
    window.show()
    sys.exit(app.exec_())
