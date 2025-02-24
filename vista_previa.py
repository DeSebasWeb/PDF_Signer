import os
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path

class VistaPrevia(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.coordenadas = []  # Lista para almacenar las coordenadas de clics
        self._zoom = 1  # Factor de zoom inicial

    def mostrar_mensaje(self, titulo, mensaje, icono=QMessageBox.Information): 
        # Nota: Usaremos la función local de la clase en main.py para mostrar mensajes.
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(icono)
        msg.exec_()

    def cargar_pdf(self, ruta_carpeta):
        """
        Busca el primer PDF en la primera subcarpeta de la carpeta dada y lo muestra.
        Si no se encuentra ningún PDF, muestra un mensaje en la vista.
        """
        if not os.path.exists(ruta_carpeta):
            self.mostrar_mensaje("Error", "La carpeta seleccionada no existe.", QMessageBox.Warning)
            return

        pdf_encontrado = None

        # Buscar en cada subcarpeta el segundo archivo PDF
        for subcarpeta in os.listdir(ruta_carpeta):
            ruta_subcarpeta = os.path.join(ruta_carpeta, subcarpeta)
            if os.path.isdir(ruta_subcarpeta):
                pdfs = []  # Lista para almacenar todos los PDFs de esta subcarpeta
                for archivo in os.listdir(ruta_subcarpeta):
                    if archivo.lower().endswith(".pdf"):
                        pdfs.append(os.path.join(ruta_subcarpeta, archivo))
                # Si existen al menos 2 archivos PDF, seleccionamos el segundo (índice 1)
                if len(pdfs) >= 2:
                    pdf_encontrado = pdfs[1]
                    break  # Salimos una vez encontrado el segundo PDF

        if pdf_encontrado:
            try:
                imagenes = convert_from_path(pdf_encontrado, first_page=1, last_page=1,
                                             poppler_path=r"C:\poppler-24.08.0\Library\bin")
                if imagenes:
                    # Convertir la imagen PIL a QImage
                    pil_image = imagenes[0]
                    data = pil_image.tobytes("raw", "RGB")
                    qimg = QImage(data, pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.scene.clear()
                    self.scene.addPixmap(pixmap)
                    self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            except Exception as e:
                self.mostrar_mensaje("Error", f"No se pudo cargar el PDF: {str(e)}", QMessageBox.Critical)
        else:
            # No se encontró ningún segundo PDF
            self.scene.clear()
            text_item = self.scene.addText("Ningún PDF encontrado para mostrar.")
            text_item.setDefaultTextColor(Qt.red)
            text_item.setScale(1.5)
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Captura el clic y guarda las coordenadas."""
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.coordenadas.append((pos.x(), pos.y()))
            print(f"Coordenada guardada: {pos.x()}, {pos.y()}")
    
    def wheelEvent(self, event):
        """Permite hacer zoom usando la rueda del mouse."""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Determinar la dirección del scroll
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self._zoom *= zoom_factor

        # Opcional: Puedes limitar el zoom mínimo y máximo
        if self._zoom < 0.2:
            self._zoom = 0.2
            zoom_factor = 1
        elif self._zoom > 5:
            self._zoom = 5
            zoom_factor = 1

        self.scale(zoom_factor, zoom_factor)
