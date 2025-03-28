# AIDA Main Widget module
# Defines the main configuration UI for the AIDA plugin

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit, QLineEdit, QComboBox, QHBoxLayout, QLabel
from ida_kernwin import PluginForm
from PyQt5.QtCore import QObject

class MainWidget(PluginForm, QObject):
    """
    Main widget for the AIDA plugin.
    Provides configuration options for the AI model and target language.
    Inherits from both PluginForm (IDA Pro) and QObject (PyQt).
    """
    def __init__(self):
        """
        Initialize the main widget.
        Sets up initial state and inherits from parent classes.
        """
        PluginForm.__init__(self)
        QObject.__init__(self)
        self.stop_flag: bool = False  # Flag to control async operations

    def OnCreate(self, form) -> None:
        """
        Called when the form is created by IDA Pro.
        Converts the IDA Pro form to a PyQt widget and populates it.
        
        Args:
            form: IDA Pro form object
        """
        self.parent: QWidget = self.FormToPyQtWidget(form)
        self.PopulateForm()

    def PopulateForm(self) -> None:
        """
        Populates the form with UI controls.
        Creates and arranges the model selector, API token input, and language selector.
        """
        # Create main layout with margins
        layout: QVBoxLayout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Create top layout for model selection and API token
        top_layout: QHBoxLayout = QHBoxLayout()

        # Model selection dropdown
        self.model_combo: QComboBox = QComboBox()
        self.model_combo.addItems(["DeepSeek-V3"])

        # API token input field
        self.token_input: QLineEdit = QLineEdit()
        self.token_input.setPlaceholderText("API token here")
        
        top_layout.addWidget(self.model_combo)
        top_layout.addWidget(self.token_input)

        # Create bottom layout for language selection
        bottom_layout: QHBoxLayout = QHBoxLayout()
        
        # Target language selection
        lang_label: QLabel = QLabel("Target Language:")
        self.lang_combo: QComboBox = QComboBox()
        self.lang_combo.addItems([
            "C++",
            "Swift",
            "Go",
            "Rust",
            "Python",
            "C#",
        ])
        
        bottom_layout.addWidget(lang_label)
        bottom_layout.addWidget(self.lang_combo)

        # Add layouts to main layout
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)
        self.parent.setLayout(layout)