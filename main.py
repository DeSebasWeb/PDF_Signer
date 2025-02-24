import sys
import fitz  # PyMuPDF
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from vista_previa import VistaPrevia
from interfaz import Ui_Dialog  # Importamos la UI generada con Qt Designer

class PDFSignerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Configurar icono de la aplicación
        if getattr(sys, 'frozen', False):  # Si se ejecuta como .exe
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icono.png")
        self.setWindowIcon(QIcon(icon_path))

        # Reemplazar el QGraphicsView placeholder "mostrar_pdf" (definido en el .ui)
        # con una instancia de VistaPrevia para manejar la vista previa interactiva.
        old_view = self.ui.mostrar_pdf
        parent = old_view.parent()
        geometry = old_view.geometry()
        # Crear instancia de VistaPrevia y establecer la misma geometría
        self.vista_previa = VistaPrevia(parent)
        self.vista_previa.setGeometry(geometry)
        self.vista_previa.setObjectName("mostrar_pdf")
        old_view.hide()  # Ocultar el QGraphicsView original

        # Conectar botones a funciones
        self.ui.btn_seleccionar_carpeta.clicked.connect(self.seleccionar_carpeta_entrada)
        self.ui.btn_firmar.clicked.connect(self.seleccionar_carpeta_salida)
        
        # Agregar una barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Variables de carpeta (se asignarán al seleccionar carpetas)
        self.carpeta_base_entrada = ""
        self.carpeta_base_salida = ""
        
        # Inicializar progressBar con mensaje
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setFormat("Listo para comenzar✅")
        
        # Aplicar estilos generales
        self.aplicar_estilos()
        
    def mostrar_mensaje(self, titulo, mensaje, icono=QMessageBox.Information):
        """Muestra un QMessageBox personalizado con estilo."""
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(icono)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
                color: black;
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
        """Aplica estilos visuales a la aplicación completa."""
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
        # También actualizamos el icono y título (aunque ya lo configuramos antes)
        self.setWindowIcon(QtGui.QIcon("icono.png"))
        self.setWindowTitle("Firma de PDFs en Lote")
        
    def seleccionar_carpeta_entrada(self):
        """Abre un diálogo para seleccionar la carpeta con los PDFs de entrada y carga la vista previa."""
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de entrada")
        if carpeta:
            self.carpeta_base_entrada = carpeta
            self.ui.lbl_ubicacion1.setText(f"Carpeta entrada: {os.path.basename(carpeta)}")
            self.statusBar.showMessage("Carpeta de entrada seleccionada", 3000)
            # Usar VistaPrevia para mostrar el primer PDF encontrado en la carpeta seleccionada
            self.vista_previa.cargar_pdf(carpeta)
        
    def seleccionar_carpeta_salida(self):
        """Abre un diálogo para seleccionar la carpeta de salida y luego inicia el proceso de firma."""
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_base_salida = carpeta
            self.ui.lbl_ubicacion2.setText(f"Carpeta salida: {os.path.basename(carpeta)}")
            self.statusBar.showMessage("Carpeta de salida seleccionada", 3000)
            self.firmar_pdfs()  # Inicia la firma de PDFs
            
    def firmar_pdfs(self):
        """Recorre las subcarpetas de la carpeta de entrada, firma los PDFs y mueve las carpetas procesadas a 'finalizado'."""
        if not self.carpeta_base_entrada or not self.carpeta_base_salida:
            self.mostrar_mensaje("Error", "⚠️ Debes seleccionar ambas carpetas antes de continuar.", QMessageBox.Warning)
            return
        
        # Obtener valores de nombre y cargo desde los QLineEdit
        nombre = self.ui.edit_nombre.text().strip()
        cargo = self.ui.edit_cargo.text().strip()
        if not nombre or not cargo:
            QMessageBox.critical(self, "Error", "⚠️ Ingresa tu nombre y cargo antes de continuar.")
            return
        
        # Confirmación antes de proceder
        respuesta = QMessageBox.question(
            self, "Confirmación",
            f"¿Deseas proceder con la firma de PDFs usando los siguientes datos?\n\nNombre: {nombre}\nCargo: {cargo}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if respuesta == QMessageBox.No:
            return
        
        # Carpeta donde se moverán las subcarpetas procesadas
        carpeta_finalizados = os.path.join(self.carpeta_base_entrada, "finalizado")
        if not os.path.exists(carpeta_finalizados):
            os.makedirs(carpeta_finalizados)
        
        tamano_fuente = 10
        # Obtenemos todas las subcarpetas (excluyendo "finalizado")
        subcarpetas = [d for d in os.listdir(self.carpeta_base_entrada)
                       if os.path.isdir(os.path.join(self.carpeta_base_entrada, d)) and d != "finalizado"]
        total = len(subcarpetas)
        procesados = 0
        
        for subcarpeta in subcarpetas:
            ruta_subcarpeta = os.path.join(self.carpeta_base_entrada, subcarpeta)
            fecha_extraida = subcarpeta[:5]  # Se extrae la fecha del nombre de la subcarpeta
            texto_firma = f"Recibido: {nombre}\n{cargo}\nFecha: {fecha_extraida}/2025"
            
            # Crear carpeta de salida para la subcarpeta procesada dentro de la carpeta seleccionada por el usuario
            carpeta_destino = os.path.join(self.carpeta_base_salida, subcarpeta + "_Firmados")
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)
            
            # Procesar cada PDF en la subcarpeta
            for archivo in os.listdir(ruta_subcarpeta):
                if archivo.endswith(".pdf"):
                    ruta_pdf = os.path.join(ruta_subcarpeta, archivo)
                    pdf = fitz.open(ruta_pdf)
                    page = pdf[0]
                    rect = page.rect
                    
                    pos_x = rect.width - 250
                    pos_y = 37
                    
                    page.insert_text((pos_x, pos_y), texto_firma,
                                     fontsize=tamano_fuente, fontname="helv", color=(0, 0, 0))
                    
                    pdf_salida = os.path.join(carpeta_destino, archivo)
                    pdf.save(pdf_salida)
                    pdf.close()
            
            # Mover la subcarpeta procesada a "finalizado"
            shutil.move(ruta_subcarpeta, os.path.join(carpeta_finalizados, subcarpeta))
            
            procesados += 1
            progreso = int((procesados / total) * 100)
            self.ui.progressBar.setValue(progreso)
            self.ui.progressBar.setFormat(f"{progreso}%")
        
        self.ui.progressBar.setFormat("✅ Proceso completado")
        self.ui.lbl_ubicacion1.setText("✅ Proceso completado. PDFs firmados correctamente.")
        self.statusBar.showMessage("Firma de PDFs completada con éxito", 5000)
        self.mostrar_mensaje("Carga completada", "Todos los PDF's se han firmado correctamente", QMessageBox.Information)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PDFSignerApp()
    ventana.show()
    sys.exit(app.exec_())
