import sys
import pymupdf
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidget, QTextEdit, QHBoxLayout, QWidget, QFileDialog, QLabel, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lista_paginas = []
        self.pdf_document = None
        self.construir_menu()
        self.setup_ui()

    def construir_menu(self):
        menu = self.menuBar()
        menu_archivo = menu.addMenu("Menu")
        menu_archivo.addAction("Abrir PDF", self.abrir_pdf)
        menu_archivo.addAction("Guardar Página como PDF",
                               self.guardar_pagina_pdf)
        menu_archivo.addAction("Extraer todo como PDF",
                               self.guardar_todas_pdfs)
        menu_archivo.addSeparator()
        menu_archivo.addAction("Salir", self.close)

    def abrir_pdf(self):
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar PDF", "", "Archivos PDF (*.pdf);;Todos los archivos (*)", options=opciones)

        if archivo:
            self.pdf_document = pymupdf.open(archivo)
            num_pages = len(self.pdf_document)
            self.lista_paginas = [
                f"Página {num + 1}" for num in range(num_pages)]
            self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Extractor Paginas PDF")
        self.setGeometry(200, 200, 800, 400)

        # Crear el widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Crear el layout horizontal
        layout = QHBoxLayout(central_widget)

        # Crear la lista y añadir elementos
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.lista_paginas)

        # Crear una etiqueta para mostrar la imagen del PDF
        self.pdf_label = QLabel()

        # Conectar la señal de selección de la lista al método que actualiza el visualizador
        self.list_widget.currentItemChanged.connect(self.update_viewer)

        # Añadir widgets al layout
        layout.addWidget(self.list_widget)
        layout.addWidget(self.pdf_label)

    def update_viewer(self, current_item):
        """Actualiza el visualizador con la página seleccionada."""
        if current_item and self.pdf_document is not None:
            # Obtener número de página
            page_number = int(current_item.text().split()[1]) - 1
            page = self.pdf_document.load_page(page_number)  # Cargar la página
            output_dir = 'temp'
            os.makedirs(output_dir, exist_ok=True)
            pix = page.get_pixmap()  # Renderizar la página como imagen
            img_path = f"{output_dir}/temp_page.png"
            pix.save(img_path)  # Guardar imagen temporalmente
            # Mostrar imagen en QLabel
            self.pdf_label.setPixmap(QPixmap(img_path).scaled(900, 700, Qt.KeepAspectRatio,Qt.SmoothTransformation))
            self.setFixedSize(700,750)

    def guardar_pagina_pdf(self):
        current_item = self.list_widget.currentItem()
        
        if not self.pdf_document:
            QMessageBox.warning(
                self, "Error", "No se ha abierto ningún documento PDF.")
            return

        if not current_item:
            QMessageBox.warning(
                self, "Error", "No se ha seleccionado ninguna página.")
            return


        try:
            page_number = int(current_item.text().split()[1]) - 1

            # Verifica que el número de página esté dentro del rango
            if page_number < 0 or page_number >= len(self.pdf_document):
                QMessageBox.warning(
                    self, "Error", "Número de página fuera de rango.")
                return

            opciones = QFileDialog.Options()
            archivo_guardado, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Página como PDF",
                f"Documento {page_number + 1}.pdf",
                "Archivos PDF (*.pdf);;Todos los archivos (*)",
                options=opciones
            )

            if archivo_guardado:
                # Crea un nuevo documento PDF
                doc_nuevo = pymupdf.open()

                # Copia la página desde el documento original al nuevo
                doc_nuevo.insert_pdf(
                    self.pdf_document, from_page=page_number, to_page=page_number)

                # Guarda el nuevo documento
                doc_nuevo.save(archivo_guardado)
                doc_nuevo.close()

                QMessageBox.information(
                    self, "Éxito", "Página guardada como PDF exitosamente.")
            else:
                QMessageBox.warning(
                    self, "Error", "No se pudo guardar la página.")

        except pymupdf.EmptyFileError as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"El archivo PDF está vacío o corrupto: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"Ocurrió un error al guardar la página: {e}")

    def guardar_todas_pdfs(self):
        if not self.pdf_document:
            QMessageBox.warning(
                self, "Error", "No se ha abierto ningún documento PDF.")
            return

        try:

            num_pages = len(self.pdf_document)
            opciones = QFileDialog.Options()
            archivo_guardado = QFileDialog.getExistingDirectory(caption="Selecione Carpeta",options=opciones)

            for num in range(num_pages):
                if archivo_guardado:
                    # Crea un nuevo documento PDF
                    doc_nuevo = pymupdf.open()

                    # Copia la página desde el documento original al nuevo
                    doc_nuevo.insert_pdf(
                        self.pdf_document, from_page=num, to_page=num)

                    # Guarda el nuevo documento
                    doc_nuevo.save(f"{archivo_guardado}/documento{num +1}.pdf")
                    doc_nuevo.close()

                else:
                    QMessageBox.warning(
                        self, "Error", "No se pudo guardar las páginas.")

            QMessageBox.information(
                        self, "Éxito", "Páginas guardadas como PDF exitosamente.")
        except pymupdf.EmptyFileError as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"Los archivos PDF están vacíos o corruptos: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"Ocurrió un error al guardar la páginas: {e}")
  
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
