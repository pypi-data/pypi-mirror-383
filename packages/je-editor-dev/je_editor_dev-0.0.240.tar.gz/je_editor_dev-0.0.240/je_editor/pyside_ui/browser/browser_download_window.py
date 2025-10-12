from PySide6.QtCore import Qt
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtWidgets import QWidget, QBoxLayout, QPlainTextEdit

from je_editor.utils.logging.loggin_instance import jeditor_logger
from je_editor.utils.multi_language.multi_language_wrapper import language_wrapper


class BrowserDownloadWindow(QWidget):

    def __init__(self, download_instance: QWebEngineDownloadRequest):
        super().__init__()
        jeditor_logger.info("Init BrowserDownloadWindow "
                            f"download_instance: {download_instance}")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.box_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.show_download_detail_plaintext = QPlainTextEdit()
        self.show_download_detail_plaintext.setReadOnly(True)
        self.setWindowTitle(language_wrapper.language_word_dict.get("browser_download_detail"))
        self.download_instance = download_instance
        self.download_instance.isFinishedChanged.connect(self.print_finish)
        self.download_instance.interruptReasonChanged.connect(self.print_interrupt)
        self.download_instance.stateChanged.connect(self.print_state)
        self.download_instance.accept()
        self.box_layout.addWidget(self.show_download_detail_plaintext)
        self.setLayout(self.box_layout)


    def print_finish(self):
        jeditor_logger.info("BrowserDownloadWindow Print Download is Finished")
        self.show_download_detail_plaintext.appendPlainText(str(self.download_instance.isFinished()))

    def print_interrupt(self):
        jeditor_logger.info("BrowserDownloadWindow Print interruptReason")
        self.show_download_detail_plaintext.appendPlainText(str(self.download_instance.interruptReason()))

    def print_state(self):
        jeditor_logger.info("BrowserDownloadWindow Print State")
        self.show_download_detail_plaintext.appendPlainText(str(self.download_instance.state()))
