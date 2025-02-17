# 📄 PDF Signer - Firma automática de PDFs

## 🚀 Descripción
Este es un script en **Python** que automatiza la firma de documentos PDF, analizando subcarpetas y organizando los archivos firmados en una estructura ordenada. Ideal para procesar múltiples PDFs de manera eficiente.

## 🛠️ Tecnologías usadas
- **Python** 🐍
- **PyMuPDF (fitz)** para manipular PDFs

## 📂 Estructura del proyecto
### 📁 pdfs_a_firmar
Carpeta donde se colocan los PDFs originales 
### 📁 pdfs_firmados 
Carpeta donde se guardan los PDFs firmados 
### 📁 finalizados
Carpeta donde se mueven los documentos ya procesados
<br>
<br>
📄 script.py # Script principal

## 🔧 Instalación y uso

1️⃣ **Clona este repositorio**  
```bash
git clone https://github.com/tu-usuario/pdf-signer.git
cd pdf-signer
```
2️⃣ **Instala las dependencias**
```bash
pip install -r requirements.txt
```
3️⃣ **Ejecuta el script**
```bash
python script.py
```
El programa recorrerá automáticamente las subcarpetas en pdfs_a_firmar, firmará los documentos y los guardará en pdfs_firmados.

## ✨ Funcionalidades
✔ Firma automáticamente todos los PDFs en una carpeta<br>
✔ Detecta subcarpetas y firma en lote<br>
✔ Organiza los archivos firmados en una nueva estructura<br>
✔ Evita firmar documentos duplicados al moverlos a una carpeta "finalizados"

## 📌 Próximos pasos
 Interfaz gráfica con PyQt 🖥️<br>
 Selector de carpetas para mayor flexibilidad 📂<br>
 Barra de progreso para mejor experiencia de usuario 🚀

## 📝 Licencia
Este proyecto es de código abierto bajo la licencia MIT.

### 📌 Autor: Sebastián López
### 💡 Si te es útil, no olvides darle ⭐ en GitHub.
