# AIDA Async Thread module
# Provides asynchronous execution capabilities for AI processing

from asyncio import new_event_loop, set_event_loop, get_event_loop
from PyQt5.QtCore import QThread, pyqtSignal

class AsyncThread(QThread):
    """
    Thread class for handling asynchronous operations.
    Inherits from PyQt's QThread and manages asyncio coroutines.
    Provides signals for communicating results back to the UI thread.
    """
    # Signal emitted when the operation completes successfully
    finished = pyqtSignal(str)
    # Signal emitted when an error occurs during operation
    error = pyqtSignal(str)

    def __init__(self, coro) -> None:
        """
        Initialize the async thread with a coroutine to run.
        
        Args:
            coro: The asyncio coroutine to execute in this thread
        """
        super().__init__()
        self.coro = coro  # Store the coroutine
        self.loop = None  # Event loop reference

    def run(self) -> None:
        """
        Thread execution method.
        Sets up an asyncio event loop and runs the coroutine to completion.
        Emits appropriate signals based on success or failure.
        """
        try:
            # Get or create an event loop for this thread
            try:
                self.loop = get_event_loop()
            except RuntimeError:
                # If no loop exists in this thread, create a new one
                self.loop = new_event_loop()
                set_event_loop(self.loop)

            # Run the coroutine to completion
            result = self.loop.run_until_complete(self.coro)
            # Emit the result to the UI thread
            self.finished.emit(result)
        except Exception as e:
            # Emit any errors to the UI thread
            self.error.emit(str(e))
        finally:
            # Clean up the event loop
            if self.loop and self.loop.is_running():
                self.loop.stop()
                self.loop.close()