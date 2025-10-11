# Default imports
import sys
import warnings
import traceback
from itertools import chain
from pathlib import Path
from importlib import resources
import os
from multiprocessing import Process

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QLabel, QLineEdit, QCheckBox, QGroupBox, QFileDialog,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSlot, pyqtSignal, QUrl, Qt
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor, QDesktopServices

# Import the necessary functions from the package
from numbers_and_brightness.analysis import numbers_and_brightness_analysis, numbers_and_brightness_batch
from numbers_and_brightness._gui_components._utils import wrap_text, show_error_message, show_info_popup, gui_logger
from numbers_and_brightness import __version__
from numbers_and_brightness._defaults import (
    DEFAULT_BACKGROUND,
    DEFAULT_SEGMENT,
    DEFAULT_DIAMETER,
    DEFAULT_FLOW_THRESHOLD,
    DEFAULT_CELLPROB_THRESHOLD,
    DEFAULT_ANALYSIS,
    DEFAULT_ERODE,
    DEFAULT_BLEACH_CORR,
    DEFAULT_USE_EXISTING_MASK,
    DEFAULT_CREATE_OVERVIEW
)

# Import GUI components
from numbers_and_brightness._gui_components._brightness_intensity import brightness_intensity_window

def resource_path() -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.dirname(__file__))

class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)

class NumbersAndBrightnessApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.file = ""
        self.folder = ""

        self.b_i_windows = []

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"Numbers and Brightness Analysis - Version {__version__}")

        # Main widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # File and folder selection buttons
        self.file_select_button = QPushButton("Select file")
        self.file_select_button.clicked.connect(self.get_file)
        main_layout.addWidget(self.file_select_button, 0, 0, 1, 2)

        self.folder_select_button = QPushButton("Select folder")
        self.folder_select_button.clicked.connect(self.get_folder)
        main_layout.addWidget(self.folder_select_button, 1, 0, 1, 2)

        # Background input
        bg_label = QLabel("Background:")
        self.background_input = QLineEdit()
        self.background_input.setText(str(DEFAULT_BACKGROUND))
        main_layout.addWidget(bg_label, 2, 0)
        main_layout.addWidget(self.background_input, 2, 1)

        # Segment checkbox
        segment_label = QLabel("Segment:")
        self.segment_input = QCheckBox()
        self.segment_input.setChecked(DEFAULT_SEGMENT)
        main_layout.addWidget(segment_label, 3, 0)
        main_layout.addWidget(self.segment_input, 3, 1)

        # Cellpose settings group
        cellpose_group = QGroupBox("Cellpose settings:")
        cellpose_layout = QGridLayout(cellpose_group)

        # Diameter input
        diameter_label = QLabel("Diameter:")
        self.diameter_input = QLineEdit()
        self.diameter_input.setText(str(DEFAULT_DIAMETER))
        cellpose_layout.addWidget(diameter_label, 0, 0)
        cellpose_layout.addWidget(self.diameter_input, 0, 1)

        # Flow threshold input
        flow_label = QLabel("Flow threshold:")
        self.flow_input = QLineEdit()
        self.flow_input.setText(str(DEFAULT_FLOW_THRESHOLD))
        cellpose_layout.addWidget(flow_label, 1, 0)
        cellpose_layout.addWidget(self.flow_input, 1, 1)

        # Cellprob threshold input
        cellprob_label = QLabel("Cellprob threshold:")
        self.cellprob_input = QLineEdit()
        self.cellprob_input.setText(str(DEFAULT_CELLPROB_THRESHOLD))
        cellpose_layout.addWidget(cellprob_label, 2, 0)
        cellpose_layout.addWidget(self.cellprob_input, 2, 1)

        main_layout.addWidget(cellpose_group, 4, 0, 1, 2)

        # Analysis checkbox
        analysis_label = QLabel("Analysis:")
        self.analysis_input = QCheckBox()
        self.analysis_input.setChecked(DEFAULT_ANALYSIS)
        main_layout.addWidget(analysis_label, 5, 0)
        main_layout.addWidget(self.analysis_input, 5, 1)

        # Erode input
        erode_label = QLabel("Erode:")
        self.erode_input = QLineEdit()
        self.erode_input.setText(str(DEFAULT_ERODE))
        main_layout.addWidget(erode_label, 6, 0)
        main_layout.addWidget(self.erode_input, 6, 1)

        # Bleach correction checkbox
        bleach_corr_label = QLabel("Bleach correction:")
        self.bleach_corr_input = QCheckBox()
        self.bleach_corr_input.setChecked(DEFAULT_BLEACH_CORR)
        main_layout.addWidget(bleach_corr_label, 7, 0)
        main_layout.addWidget(self.bleach_corr_input, 7, 1)

        # Use existing masks checkbox
        use_existing_label = QLabel("Use existing segmentation:")
        self.use_existing_input = QCheckBox()
        self.use_existing_input.setChecked(DEFAULT_USE_EXISTING_MASK)
        main_layout.addWidget(use_existing_label, 8, 0)
        main_layout.addWidget(self.use_existing_input, 8, 1)

        # Create overview checkbox
        create_overview_label = QLabel("Create overview:")
        self.create_overview_input = QCheckBox()
        self.create_overview_input.setChecked(DEFAULT_CREATE_OVERVIEW)
        main_layout.addWidget(create_overview_label, 9, 0)
        main_layout.addWidget(self.create_overview_input, 9, 1)

        # Process buttons
        self.process_file_button = QPushButton("Process file")
        self.process_file_button.clicked.connect(self.process_file)
        main_layout.addWidget(self.process_file_button, 10, 0, 1, 2)

        self.process_folder_button = QPushButton("Process folder")
        self.process_folder_button.clicked.connect(self.process_folder)
        main_layout.addWidget(self.process_folder_button, 11, 0, 1, 2)

        # Store buttons for enabling/disabling
        self.select_buttons = [self.file_select_button, self.folder_select_button]
        self.process_buttons = [self.process_file_button, self.process_folder_button]

        self.create_menu()

    @pyqtSlot()
    def create_menu(self):
        menu_bar = self.menuBar()

        # Tools
        file_menu = menu_bar.addMenu("Tools")

        b_i_action = QAction("Brightness - Intensity", self)
        b_i_action.triggered.connect(self.open_b_i)
        file_menu.addAction(b_i_action)

        b_i_action = QAction("Cellpose", self)
        b_i_action.triggered.connect(self.open_cellpose)
        file_menu.addAction(b_i_action)

        # About
        file_menu = menu_bar.addMenu("About")

        github_action = QAction("User guide", self)
        github_action.triggered.connect(self.open_documentation)
        file_menu.addAction(github_action)

        github_action = QAction("GitHub", self)
        github_action.triggered.connect(self.open_github)
        file_menu.addAction(github_action)

    @pyqtSlot()
    def open_b_i(self):
        self.b_i_window = brightness_intensity_window()
        self.b_i_window.show()
        self.b_i_windows.append(self.b_i_window)

    def open_cellpose(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Starting Cellpose")
        msg_box.setText("Initializing Cellpose GUI, this might take a few seconds.")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowModality(Qt.WindowModality.NonModal)
        msg_box.show()

        from cellpose.gui import gui

        p = Process(target=gui.run)
        p.daemon = True
        p.start()

    @pyqtSlot()
    def open_github(self):
        url = QUrl("https://github.com/Cellular-Imaging-Amsterdam-UMC/Numbers-and-Brightness")
        QDesktopServices.openUrl(url)

    @pyqtSlot()
    def open_documentation(self):
        url = QUrl("https://cellular-imaging-amsterdam-umc.github.io/Numbers-and-Brightness/")
        QDesktopServices.openUrl(url)

    @pyqtSlot()
    def get_file(self):
        """Open file dialog to select a file"""
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.file = filename
            self.file_select_button.setText(wrap_text(filename, 50))

    @pyqtSlot()
    def get_folder(self):
        """Open file dialog to select a folder"""
        foldername = QFileDialog.getExistingDirectory(self, "Select Folder")
        if foldername:
            self.folder = foldername
            self.folder_select_button.setText(wrap_text(foldername, 50))

    def _set_buttons_enabled(self, enabled: bool):
        """Helper method to enable/disable all buttons"""
        for button in chain(self.select_buttons, self.process_buttons):
            button.setEnabled(enabled)

    """File analysis functions"""
    def process_file_call(self):
        numbers_and_brightness_analysis(
            file=self.file,
            background=float(self.background_input.text()),
            segment=self.segment_input.isChecked(),
            diameter=int(self.diameter_input.text()),
            flow_threshold=float(self.flow_input.text()),
            cellprob_threshold=float(self.cellprob_input.text()),
            analysis=self.analysis_input.isChecked(),
            erode=int(self.erode_input.text()),
            bleach_corr=self.bleach_corr_input.isChecked(),
            use_existing_mask=self.use_existing_input.isChecked()
        )
        print(f"Processed: {self.file}")

    def process_file_finished(self):
        show_info_popup(parent=self, title="Finished", message=f"Finished analysis of: {self.file}")
        self._set_buttons_enabled(True)

    def process_file_error(self, error):
        show_error_message(parent=self, message=str(error))
        self._set_buttons_enabled(True)

    @pyqtSlot()
    def process_file(self):
        """Process a single file"""
        if not self.file:
            print("Select a file")
            return
            
        self._set_buttons_enabled(False)
        self.worker = Worker(fn=self.process_file_call)

        self.worker.finished.connect(self.process_file_finished)
        self.worker.error.connect(self.process_file_error)

        self.worker.start()

    """Folder analysis functions"""
    def process_folder_call(self):
        numbers_and_brightness_batch(
            folder=self.folder,
            background=float(self.background_input.text()),
            segment=self.segment_input.isChecked(),
            diameter=int(self.diameter_input.text()),
            flow_threshold=float(self.flow_input.text()),
            cellprob_threshold=float(self.cellprob_input.text()),
            analysis=self.analysis_input.isChecked(),
            erode=int(self.erode_input.text()),
            bleach_corr=self.bleach_corr_input.isChecked(),
            create_overviews=self.create_overview_input.isChecked(),
            use_existing_mask=self.use_existing_input.isChecked()
        )
        print(f"Processed: {self.folder}")

    def process_folder_finished(self):
        show_info_popup(parent=self, title="Finished", message=f"Finished analysis of: {self.folder}")
        self._set_buttons_enabled(True)

    def process_folder_error(self, error):
        show_error_message(parent=self, message=str(error))
        self._set_buttons_enabled(True)

    @pyqtSlot()
    def process_folder(self):
        """Process a folder"""
        if not self.folder:
            print("Select a folder")
            return
            
        self._set_buttons_enabled(False)
        self.worker = Worker(fn=self.process_folder_call)

        self.worker.finished.connect(self.process_folder_finished)
        self.worker.error.connect(self.process_folder_error)

        self.worker.start()

@gui_logger()
def nb_gui():
    """Initialize and run the GUI application"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)    # Catches matplotlib plt gui warnings
        app = QApplication(sys.argv)

        app.setStyle('Fusion')

        # Set up dark palette
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))

        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))

        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))

        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))

        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))

        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))

        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))

        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        app.setPalette(dark_palette)

        icon_path = os.path.join(resource_path(), '_gui_components', 'nb_icon.ico')
        app.setWindowIcon(QIcon(str(icon_path)))
        window = NumbersAndBrightnessApp()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    nb_gui()