#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


from functools import partial
import math
from pathlib import Path
import typing

try:
    from os import process_cpu_count
except ImportError:  # Py <3.13 compatibility
    from os import cpu_count as process_cpu_count

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QMarginsF, QSizeF, Signal, QSize, Slot, QPersistentModelIndex, QThreadPool
from PySide6.QtGui import QPainter, QPdfWriter, QPageSize, QImage, QColor
from PySide6.QtPrintSupport import QPrinter


if typing.TYPE_CHECKING:
    from mtg_proxy_printer.ui.main_window import MainWindow
    from mtg_proxy_printer.ui.dialogs import SavePDFDialog

from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.units_and_sizes import RESOLUTION
import mtg_proxy_printer.meta_data
from mtg_proxy_printer.settings import settings
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.page_scene.page_scene import RenderMode, PageScene
from mtg_proxy_printer.logger import get_logger
import mtg_proxy_printer.units_and_sizes
logger = get_logger(__name__)
del get_logger

RenderHint = QPainter.RenderHint
Format = QImage.Format

__all__ = [
    "export_pdf",
    "create_printer",
    "Renderer",
    "PNGRenderer",
]

PNGEncoderThreadLimit = max(1, process_cpu_count()-1)


class PNGRenderer(AsyncTask):
    def __init__(self, main_window: "MainWindow|None", document: Document, file_path: str):
        super().__init__(main_window)
        self.document = document
        self.file_path = Path(file_path)
        self.page_count = document.rowCount()
        self.completed = 0

    def run(self):
        document = self.document
        file_path = self.file_path
        page_count = self.page_count
        if not page_count:  # No pages in document
            logger.error("Tried to export a document with zero pages. Aborting.")
            self.task_completed.emit()
            return
        logger.info(f'Exporting document with {document.rowCount()} pages as PNG image sequence to "{file_path}"')
        page_size = document.page_layout.to_page_layout(RenderMode.ON_PAPER).pageSize().sizePixels(
            round(RESOLUTION.magnitude))
        pool = QThreadPool(self, maxThreadCount=PNGEncoderThreadLimit)
        scene = PageScene(document, RenderMode.ON_PAPER, self)
        dots_per_meter = round(RESOLUTION.to("pixel/meter").magnitude)
        background_color = settings["export"].get_color("png-background-color")
        number_width = len(str(page_count))
        parent = file_path.parent
        self.task_begins.emit(page_count, self.tr("Export as PNGs:", "Progress bar label text"))
        self.ui_lock_acquire.emit()
        for page_nr in range(page_count):
            file_name = f"{file_path.stem}-{str(page_nr + 1).zfill(number_width)}.png"
            output_path = str(parent / file_name)
            image = self._create_image(page_size, background_color, dots_per_meter)
            painter = QPainter(image)
            painter.setRenderHint(RenderHint.LosslessImageRendering, True)
            page_index = QPersistentModelIndex(document.index(page_nr, 0))
            scene.on_current_page_changed(page_index)
            scene.render(painter)
            painter.end()
            pool.start(partial(self._compress_single_image, image, output_path))
        self.ui_lock_release.emit()
        pool.waitForDone()
        self.task_completed.emit()

    @staticmethod
    def _create_image(page_size: QSize, background_color: QColor, dots_per_meter: int):
        # 255 is solid. So avoid adding the alpha channel, if it won't be used.
        image_format = Format.Format_RGB888 if background_color.alpha() == 255 else Format.Format_RGBA8888
        image = QImage(page_size, image_format)
        image.setDotsPerMeterX(dots_per_meter)
        image.setDotsPerMeterY(dots_per_meter)
        image.fill(background_color)
        return image

    def _compress_single_image(self, image: QImage, output_path: str):
        image.save(output_path, "PNG", 0)
        self.advance_progress.emit()


def export_pdf(document: Document, file_path: str, parent: "SavePDFDialog"):
    # TODO: Deprecate this and merge logic into the PDFPrinter class
    main_window = parent.parent()
    total_pages = document.rowCount()
    pages_to_print = settings["export"].getint("pdf-page-count-limit") or total_pages
    if not pages_to_print:  # No pages in document. Return now, to avoid dividing by zero
        logger.error("Tried to export a document with zero pages as a PDF. Aborting.")
        return
    logger.info(f'Exporting document with {total_pages} pages as PDF to "{file_path}"')
    total_documents = math.ceil(total_pages/pages_to_print)
    export_progress = AsyncTask()
    main_window.progress_bar_manager.add_task(export_progress)
    export_progress.task_begins.emit(
        total_pages, QApplication.translate("export_pdf", "Write PDF:", "Progress label"))
    QApplication.processEvents()
    for document_index in range(total_documents):
        logger.info(f"Creating PDF ({document_index+1}/{total_documents}) with up to {pages_to_print} pages.")
        PDFPrinter(
            document, file_path, export_progress.advance_progress, parent, document_index, pages_to_print
        ).run()
    export_progress.task_completed.emit()
    QApplication.processEvents()


def create_printer(renderer: "Renderer") -> QPrinter:
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    layout = renderer.document.page_layout
    page_layout = layout.to_page_layout(renderer.render_mode)
    if not printer.setPageLayout(page_layout):
        logger.error(
            f"Setting page layout failed! "
            f"Layout: page_size={page_layout.pageSize().size(QPageSize.Unit.Millimeter)}, "
            f"orientation={page_layout.orientation()}, "
            f"margins={layout.margin_left, layout.margin_top, layout.margin_right, layout.margin_bottom}")
    # magnitude returns a float by default, so round to int to avoid a TypeError
    printer.setResolution(round(mtg_proxy_printer.units_and_sizes.RESOLUTION.magnitude))
    # Disable duplex printing by default
    printer.setDuplex(QPrinter.DuplexMode.DuplexNone)
    printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
    if RenderMode.IMPLICIT_MARGINS not in renderer.render_mode:
        printer.setFullPage(True)
    return printer


class PDFPrinter(QPdfWriter):
    """
    Exports the given document to PDF.
    Can be given an optional index and length parameter to only export a chunk of the document for splitting purposes.
    """

    def __init__(self, document: Document, file_path: str, advance_signal: Signal, parent: QObject = None,
                 document_index: int = 0, pages_to_print: int = None):
        """
        Constructs a new PDFPrinter.
        :param document: Document to export
        :param file_path: file path for the PDF output. If pages_to_print is set and less than the total page count,
          the output file will be numbered, by appending a dash-separated numerical suffix to the file name stem.
        :param parent: Qt object parent
        :param document_index: Document sequence number. Used to compute the range of pages to be exported
        :param pages_to_print: Number of pages to export. Default value None means "all pages"
        """
        self.advance_progress = advance_signal
        self.document = document
        self.document_index = document_index
        self.pages_to_print = pages_to_print = pages_to_print or document.rowCount()
        self.landscape_workaround_enabled = settings["export"].getboolean("landscape-compatibility-workaround")
        if pages_to_print < document.rowCount():
            # Determine the number of digits required to properly sort all documents, without having to rely on
            # external support for natural sorting
            suffix_length = len(str(math.ceil(document.rowCount() / pages_to_print)))
            # Add one to the document_index for human-readable counting starting at 1
            suffix = str(document_index+1).zfill(suffix_length)
            path = Path(file_path)
            file_path = str(path.with_stem(f"{path.stem}-{suffix}"))
        super().__init__(file_path)
        self.setParent(parent)
        self.setCreator(f"{mtg_proxy_printer.meta_data.PROGRAMNAME}, v{mtg_proxy_printer.meta_data.__version__}")
        self.painter = QPainter()
        # magnitude returns a float by default, so round to int to avoid a TypeError
        self.setResolution(round(mtg_proxy_printer.units_and_sizes.RESOLUTION.magnitude))
        self.setPageSize(self._to_page_size(document.page_layout))
        # Prevent downscaling the page content
        self.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.scene = PageScene(document, RenderMode.ON_PAPER, self)
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _to_page_size(self, layout: PageLayoutSettings) -> QPageSize:
        """Converts PageLayoutSettings to QPageSize"""
        size = QSizeF(layout.page_width.magnitude, layout.page_height.magnitude)
        if layout.page_width > layout.page_height and self.landscape_workaround_enabled:
            size.transpose()
        return QPageSize(size, QPageSize.Unit.Millimeter)

    def run(self):
        logger.info("Begin rendering PDF document.")
        layout = self.document.page_layout
        scaling = 1
        self.painter.begin(self)
        if layout.page_width > layout.page_height and self.landscape_workaround_enabled:
            scaling = self.scene.width()/self.scene.height()
            self.painter.rotate(90)
            self.painter.translate(0, -self.scene.height())
        self.painter.setRenderHint(RenderHint.LosslessImageRendering)  # Prevent avoidable image degradation
        self.painter.scale(
                scaling*self.logicalDpiX()/self.resolution(),
                scaling*self.logicalDpiY()/self.resolution(),
            )
        first_index = self.document_index * self.pages_to_print
        last_index = min((self.document_index + 1) * self.pages_to_print, self.document.rowCount())

        for page_number in range(first_index, last_index):
            logger.debug(f"Rendering page {page_number+1}/{self.document.rowCount()}")
            self._switch_to_page(page_number)
            self.scene.render(self.painter)
            if page_number + 1 < last_index:  # Avoid including a trailing, empty page
                self.newPage()
            self.advance_progress.emit()
            QApplication.processEvents()
        self.painter.end()
        logger.info("Writing document finished.")

    def _switch_to_page(self, page_number: int):
        """Render the given page on the internal scene"""
        index = QPersistentModelIndex(self.document.index(page_number, 0))
        self.scene.on_current_page_changed(index)


class Renderer(QObject):

    def __init__(self, document: Document, parent: QObject = None):
        super().__init__(parent)
        self.document = document
        self.render_mode = RenderMode.ON_PAPER
        if not settings["printer"].getboolean("borderless-printing"):
            self.render_mode |= RenderMode.IMPLICIT_MARGINS
        self.scene = PageScene(document, self.render_mode, self)

    @Slot(QPrinter)
    def print_document(self, printer: QPrinter):
        logger.info("Begin printing document.")
        landscape_workaround_enabled = settings["printer"].getboolean("landscape-compatibility-workaround")
        is_landscape_document = self.scene.width() > self.scene.height()
        painter = QPainter(printer)
        if is_landscape_document and landscape_workaround_enabled:
            painter.rotate(90)
            painter.translate(0, -self.scene.height())
            scaling = self.scene.width()/self.scene.height()
            painter.scale(scaling, scaling)
        painter.setRenderHint(RenderHint.LosslessImageRendering)
        page_count = self.document.rowCount()
        for index in range(page_count):
            logger.debug(f"Printing page {index+1}/{page_count}")
            self.scene.on_current_page_changed(QPersistentModelIndex(self.document.index(index, 0)))
            self.scene.render(painter)
            if index+1 < page_count:
                printer.newPage()
        painter.end()
        logger.info("Printing document finished.")
