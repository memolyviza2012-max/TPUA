import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core')))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFileDialog, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from tpua_engine import TPUAEngine

DARK_SS = """
QMainWindow, QWidget, QDialog { background: #1e1e2e; color: #cdd6f4; }
QLineEdit, QTextEdit { background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 6px; font-size: 14px; }
QPushButton { background: #45475a; color: #cdd6f4; border: none; border-radius: 4px; padding: 8px 16px; font-size: 13px; font-weight: bold; }
QPushButton:hover { background: #585b70; }
QPushButton:disabled { background: #313244; color: #a6adc8; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; padding-top: 14px; font-weight: bold; color: #89b4fa; }
"""

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class TPUAApp(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tpua.app.1.0')
        except:
            pass
        self.setWindowTitle("TPUA: Universal PUA Hybrid Converter")
        self.resize(700, 450)
        self.setStyleSheet(DARK_SS)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "TPUA.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.engine = TPUAEngine()
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # File Group
        grp_file = QGroupBox("File Selection")
        l_file = QVBoxLayout(grp_file)
        
        h_in = QHBoxLayout()
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Select Input File (.txt, .csv, .json)...")
        btn_in = QPushButton("Browse")
        btn_in.clicked.connect(self.browse_input)
        h_in.addWidget(self.txt_input)
        h_in.addWidget(btn_in)
        l_file.addLayout(h_in)
        
        h_out = QHBoxLayout()
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText("Select Output File...")
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_output)
        h_out.addWidget(self.txt_output)
        h_out.addWidget(btn_out)
        l_file.addLayout(h_out)
        
        layout.addWidget(grp_file)
        
        # Action Group
        grp_action = QGroupBox("Action")
        l_action = QHBoxLayout(grp_action)
        
        self.btn_encode = QPushButton("Encode (Thai -> PUA)")
        self.btn_encode.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-size: 14px;")
        self.btn_encode.clicked.connect(self.encode_file)
        
        self.btn_decode = QPushButton("Decode (PUA -> Thai)")
        self.btn_decode.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-size: 14px;")
        self.btn_decode.clicked.connect(self.decode_file)
        
        l_action.addWidget(self.btn_encode)
        l_action.addWidget(self.btn_decode)
        layout.addWidget(grp_action)
        
        # Log
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #181825; color: #a6adc8; font-family: Consolas, monospace;")
        layout.addWidget(self.txt_log)
        
        self.log(f"TPUA Engine Loaded. Standard Map: {len(self.engine.standard)} | Contextual: {len(self.engine.contextual)}", "#a6e3a1")

    def log(self, text, color="#cdd6f4"):
        self.txt_log.append(f'<span style="color:{color};">{text}</span>')

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "All Files (*.*)")
        if path:
            self.txt_input.setText(path)
            if not self.txt_output.text():
                base, ext = os.path.splitext(path)
                self.txt_output.setText(f"{base}_pua{ext}")
                
    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "All Files (*.*)")
        if path:
            self.txt_output.setText(path)

    def read_file(self):
        path = self.txt_input.text()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Input file not found!")
            return None
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot read file:\n{e}")
                return None
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not read file (might be locked by another program):\n{e}")
            return None

    def save_file(self, content):
        path = self.txt_output.text()
        if not path: return False
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            self.log(f"Saved to: {path}", "#a6e3a1")
            return True
        except Exception as e:
            self.log(f"Error saving: {e}", "#f38ba8")
            return False

    def _set_buttons_enabled(self, enabled):
        self.btn_encode.setEnabled(enabled)
        self.btn_decode.setEnabled(enabled)

    def encode_file(self):
        text = self.read_file()
        if text is None: return
        
        self.log("Encoding Thai to PUA... Please wait...", "#89b4fa")
        self._set_buttons_enabled(False)
        
        def run_encode():
            original_pua = sum(1 for c in text if 0xF000 <= ord(c) <= 0xF8FF)
            encoded = self.engine.encode(text)
            final_pua = sum(1 for c in encoded if 0xF000 <= ord(c) <= 0xF8FF)
            return encoded, original_pua, final_pua
            
        def on_success(res):
            encoded, original_pua, final_pua = res
            self.log(f"Encoded! Original PUA: {original_pua} -> Final PUA: {final_pua} (+{final_pua - original_pua})", "#f9e2af")
            self.save_file(encoded)
            self._set_buttons_enabled(True)
            
        def on_error(err):
            self.log(f"Error encoding: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
            
        worker = Worker(run_encode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def decode_file(self):
        text = self.read_file()
        if text is None: return
        
        self.log("Decoding PUA to Thai... Please wait...", "#cba6f7")
        self._set_buttons_enabled(False)
        
        def run_decode():
            original_pua = sum(1 for c in text if 0xF000 <= ord(c) <= 0xF8FF)
            decoded = self.engine.decode(text)
            final_pua = sum(1 for c in decoded if 0xF000 <= ord(c) <= 0xF8FF)
            return decoded, original_pua, final_pua
            
        def on_success(res):
            decoded, original_pua, final_pua = res
            self.log(f"Decoded! Original PUA: {original_pua} -> Final PUA: {final_pua} (-{original_pua - final_pua})", "#f9e2af")
            self.save_file(decoded)
            self._set_buttons_enabled(True)
            
        def on_error(err):
            self.log(f"Error decoding: {err}", "#f38ba8")
            self._set_buttons_enabled(True)
            
        worker = Worker(run_decode)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TPUAApp()
    window.show()
    sys.exit(app.exec())
