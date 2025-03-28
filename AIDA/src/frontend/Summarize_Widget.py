# AIDA Summarize Widget module
# Defines the UI for displaying and processing pseudocode with AI translation

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit
from src.helpers.Async_Thread import AsyncThread
from src.backend.AI_Handler import AIHandler
from ida_kernwin import PluginForm

class SummarizeWidget(PluginForm):
    """
    Widget for displaying pseudocode and its AI-translated version.
    Inherits from IDA Pro's PluginForm.
    Handles the asynchronous processing of code with the AI model.
    """
    def __init__(self, main_widget):
        """
        Initialize the summarize widget.
        
        Args:
            main_widget: Reference to the main AIDA widget for configuration access
        """
        super().__init__()
        self.stop_flag: bool = False  # Flag to control async operations
        self.responseTE = None  # Text edit widget for displaying the response
        self.main_widget = main_widget  # Reference to main widget for configuration
        self.ai_handler: AIHandler = AIHandler()  # AI handler for processing requests
        self._async_thread = None  # Thread for asynchronous processing

    def OnCreate(self, form) -> None:
        """
        Called when the form is created by IDA Pro.
        Converts the IDA Pro form to a PyQt widget and populates it.
        
        Args:
            form: IDA Pro form object
        """
        try:
            self.parent: QWidget = self.FormToPyQtWidget(form)
            self.PopulateForm()
        except Exception as e:
            print(f"[AIDA][ERROR] Error in OnCreate: {str(e)}")

    def PopulateForm(self) -> None:
        """
        Populates the form with UI controls.
        Creates a text edit widget for displaying the AI response.
        """
        try:
            # Create main layout with margins
            layout: QVBoxLayout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)

            # Create text edit for displaying the AI response
            self.responseTE: QTextEdit = QTextEdit()
            self.responseTE.setReadOnly(True)
            self.responseTE.setPlaceholderText("AI Thinking...\n\nTip: Ctrl + Mouse Wheel to zoom :3")
            self.responseTE.setLineWrapMode(QTextEdit.NoWrap)
            
            # Set dark theme styling for the text edit
            self.responseTE.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: none;
                }
            """)
            
            layout.addWidget(self.responseTE)
            self.parent.setLayout(layout)
        except Exception as e:
            print(f"[AIDA][ERROR] Error in PopulateForm: {str(e)}")

    def __on_ai_response(self, response: str) -> None:
        """
        Callback for handling successful AI responses.
        Sets the response text and cleans up the async thread.
        
        Args:
            response: The AI-generated response text
        """
        if self.responseTE:
            self.responseTE.setPlainText(response)
            self._cleanup_thread()

    def __on_ai_error(self, error: str) -> None:
        """
        Callback for handling errors during AI processing.
        Displays the error and cleans up the async thread.
        
        Args:
            error: Error message text
        """
        if self.responseTE:
            self.responseTE.setPlainText(f"{error}")
            self._cleanup_thread()

    def _cleanup_thread(self) -> None:
        """
        Clean up the async thread after processing is complete.
        Stops and waits for the thread to finish, then clears the reference.
        """
        if self._async_thread:
            self._async_thread.quit()
            self._async_thread.wait()
            self._async_thread = None

    def set_pseudocode(self, code: str) -> None:
        """
        Set the pseudocode to process and start the AI translation.
        Gets configuration from the main widget and starts asynchronous processing.
        
        Args:
            code: Pseudocode to be processed by the AI
        """
        if self.responseTE:
            try:
                # Clean up any existing thread
                if self._async_thread:
                    self._cleanup_thread()

                # Check if the main widget is initialized
                if not self.main_widget:
                    self.responseTE.setPlainText("Plugin widget is not initialized. Press Alt + T first. Then try again")
                    return

                # Get configuration from the main widget
                selected_model: str = self.main_widget.model_combo.currentText()
                target_language: str = self.main_widget.lang_combo.currentText()
                api_key: str = self.main_widget.token_input.text()

                # Validate required fields
                if not api_key:
                    self.responseTE.setPlainText("API key is required")
                    return

                # Create and start the async thread for AI processing
                self._async_thread: AsyncThread = AsyncThread(
                    self.ai_handler.process_request(
                        model_name=selected_model,
                        pseudocode=code,
                        target_language=target_language,
                        api_key=api_key
                    )
                )
                self._async_thread.finished.connect(self.__on_ai_response)
                self._async_thread.error.connect(self.__on_ai_error)
                self._async_thread.start()

            except Exception as e:
                # Handle specific error cases
                if isinstance(e, RuntimeError):
                    self.responseTE.setPlainText("Plugin widget was closed. Press Alt + T to reopen it. Then try again")
                    self.main_widget = None
                else:
                    self.responseTE.setPlainText(f"Error: {str(e)}")