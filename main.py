import sys
import fitz  # PyMuPDF
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QStatusBar
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from interfaz import Ui_Dialog  # Importamos la UI generada

class PDFSignerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # Obtener la ruta correcta del icono
        if getattr(sys, 'frozen', False):  # Si está ejecutando como .exe
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)  # En modo normal (script)

        icon_path = os.path.join(base_path, "icono.png")
        self.setWindowIcon(QIcon(icon_path))

        # Conectar botones a funciones
        self.ui.btn_seleccionar_carpeta.clicked.connect(self.seleccionar_carpeta_entrada)
        self.ui.btn_firmar.clicked.connect(self.seleccionar_carpeta_salida)
        
        # Agregar una barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Variables de carpeta
        self.carpeta_base_entrada = ""
        self.carpeta_base_salida = ""

        # Inicializar progressBar con mensaje
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setFormat("Listo para comenzar✅")

        # Aplicar estilos
        self.aplicar_estilos()

    def mostrar_mensaje(self, titulo, mensaje, icono=QMessageBox.Information):
        """Muestra un QMessageBox personalizado."""
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(icono)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        msg.exec_()

    def aplicar_estilos(self):
        """Aplica estilos visuales a la interfaz."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 10px;
            }
            QLineEdit {
                border: 2px solid #5E81AC;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                background-color: #ECEFF4;
                selection-background-color: #81A1C1;
            }
            QLineEdit:focus {
                border: 2px solid #81A1C1;
                background-color: #D8DEE9;
            }
        """)
        self.setWindowIcon(QtGui.QIcon("icono.png"))
        self.setWindowTitle("Firma de PDFs en Lote")

    def seleccionar_carpeta_entrada(self):
        """Abre un diálogo para seleccionar la carpeta con los PDFs de entrada."""
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de entrada")
        if carpeta:
            self.carpeta_base_entrada = carpeta
            self.ui.lbl_ubicacion1.setText(f"Carpeta entrada: {os.path.basename(carpeta)}")
    
    def seleccionar_carpeta_salida(self):
        """Abre un diálogo para seleccionar la carpeta donde se guardarán los PDFs firmados."""
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_base_salida = carpeta
            self.ui.lbl_ubicacion2.setText(f"Carpeta salida: {os.path.basename(carpeta)}")
            self.firmar_pdfs()  # Llamamos a la función para firmar PDFs después de seleccionar la salida
            
    

    def firmar_pdfs(self):
        """Ejecuta el proceso de firma de PDFs."""
        if not self.carpeta_base_entrada or not self.carpeta_base_salida:
            self.mostrar_mensaje("Error", "⚠️ Debes seleccionar ambas carpetas antes de continuar.", QMessageBox.Warning)
            return
        
        # Obtener valores ingresados en los campos de texto
        nombre = self.ui.edit_nombre.text().strip()
        cargo = self.ui.edit_cargo.text().strip()
        
        # Validar que no estén vacíos
        if not nombre or not cargo:
            QMessageBox.critical(self, "Error", "⚠️ Ingresa tu nombre y cargo antes de continuar.")
            return

        # Confirmación antes de proceder
        respuesta = QMessageBox.question(
            self, "Confirmación", f"¿Deseas proceder con la firma de PDFs usando los siguientes datos?\n\nNombre: {nombre}\nCargo: {cargo}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.No:
            return

        carpeta_finalizados = os.path.join(self.carpeta_base_entrada, "finalizado")
        if not os.path.exists(carpeta_finalizados):
            os.makedirs(carpeta_finalizados)

        tamano_fuente = 10
        
        # Obtener todas las subcarpetas dentro de la carpeta de entrada
        subcarpetas = [d for d in os.listdir(self.carpeta_base_entrada) if os.path.isdir(os.path.join(self.carpeta_base_entrada, d)) and d != "finalizado"]
        total = len(subcarpetas)
        procesados = 0

        for subcarpeta in subcarpetas:
            ruta_subcarpeta = os.path.join(self.carpeta_base_entrada, subcarpeta)
            fecha_extraida = subcarpeta[:5]  # Extraer la fecha desde el nombre de la carpeta
            texto_firma = f"Recibido: {nombre} \n{cargo}\nFecha: {fecha_extraida}/2025"

            # Crear la carpeta de salida para los PDFs firmados dentro de la carpeta seleccionada por el usuario
            carpeta_salida = os.path.join(self.carpeta_base_salida, subcarpeta + "_Firmados")
            if not os.path.exists(carpeta_salida):
                os.makedirs(carpeta_salida)

            for archivo in os.listdir(ruta_subcarpeta):
                if archivo.endswith(".pdf"):
                    ruta_pdf = os.path.join(ruta_subcarpeta, archivo)
                    pdf = fitz.open(ruta_pdf)
                    page = pdf[0]
                    rect = page.rect  # Obtener dimensiones de la página

                    # Posición de la firma en la parte superior derecha del PDF
                    pos_x = rect.width - 250
                    pos_y = 37

                    # Insertar la firma en la primera página
                    page.insert_text((pos_x, pos_y), texto_firma, fontsize=tamano_fuente, fontname="helv", color=(0, 0, 0))

                    # Guardar el PDF firmado en la carpeta de salida
                    pdf_salida = os.path.join(carpeta_salida, archivo)
                    pdf.save(pdf_salida)
                    pdf.close()

            # Mover la carpeta procesada a la carpeta "finalizado"
            shutil.move(ruta_subcarpeta, os.path.join(carpeta_finalizados, subcarpeta))

            procesados += 1
            progreso = int((procesados / total) * 100)
            self.ui.progressBar.setValue(progreso)
            self.ui.progressBar.setFormat(f"{progreso}%")
        
        self.ui.progressBar.setFormat("✅ Proceso completado")

        # Mostrar mensaje de éxito
        self.mostrar_mensaje("Proceso Completado", "✅ Todos los PDFs han sido firmados exitosamente.", QMessageBox.Information)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PDFSignerApp()
    ventana.show()
    sys.exit(app.exec_())
