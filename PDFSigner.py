import fitz  # PyMuPDF
import os
import shutil  # Para mover carpetas

# Configuración de rutas
carpeta_base_entrada = "/Users/sebastianlopez/Desktop/pdfs_a_firmar"
carpeta_base_salida = "/Users/sebastianlopez/Desktop/pdfs_firmados"
carpeta_finalizados = os.path.join(carpeta_base_entrada, "finalizado")  # Carpeta donde se moverán las subcarpetas procesadas
tamano_fuente = 10  # Tamaño del texto

# Crear la carpeta de salida si no existe
if not os.path.exists(carpeta_base_salida):
    os.makedirs(carpeta_base_salida)
    print(f"📁 Carpeta base de salida creada: {carpeta_base_salida}")

# Crear la carpeta "finalizado" si no existe
if not os.path.exists(carpeta_finalizados):
    os.makedirs(carpeta_finalizados)
    print(f"📁 Carpeta 'finalizado' creada para mover documentos ya procesados.")

# Recorrer todas las subcarpetas dentro de la carpeta base de entrada
for subcarpeta in os.listdir(carpeta_base_entrada):
    ruta_subcarpeta = os.path.join(carpeta_base_entrada, subcarpeta)

    if os.path.isdir(ruta_subcarpeta) and subcarpeta != "finalizado":  # Verifica si es carpeta y no es "finalizado"
        fecha_extraida = subcarpeta[:5]  # Extrae los primeros 5 caracteres como fecha
        texto_firma = f"Recibido Tu nombre\nTu cargo\nFecha: {fecha_extraida}/2025"

        # Crear la subcarpeta de salida dentro de "pdfs_firmados"
        carpeta_salida = os.path.join(carpeta_base_salida, subcarpeta + "_Firmados")
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
            print(f"📁 Subcarpeta creada: {carpeta_salida}")

        # Procesar cada PDF dentro de la subcarpeta actual
        for archivo in os.listdir(ruta_subcarpeta):
            if archivo.endswith(".pdf"):
                ruta_pdf = os.path.join(ruta_subcarpeta, archivo)
                pdf = fitz.open(ruta_pdf)

                # Insertar el texto en la primera página
                page = pdf[0]  # Primera página
                rect = page.rect  # Dimensiones de la página
                
                # Posicionar el texto en la esquina superior derecha
                margen_x = 50  
                margen_y = 37  
                pos_x = rect.width - 200 - margen_x  
                pos_y = margen_y

                # Insertar el texto
                page.insert_text(
                    (pos_x, pos_y),
                    texto_firma,
                    fontsize=tamano_fuente,
                    fontname="helv",
                    color=(0, 0, 0)  # Negro
                )

                # Guardar el PDF firmado en la carpeta de salida
                pdf_salida = os.path.join(carpeta_salida, archivo)
                pdf.save(pdf_salida)
                pdf.close()
                print(f"✅ PDF firmado: {archivo}")

        # Mover la subcarpeta original a la carpeta "finalizado"
        destino_finalizado = os.path.join(carpeta_finalizados, subcarpeta)
        if not os.path.exists(destino_finalizado):  # Asegurar que no se sobrescriba una existente
            shutil.move(ruta_subcarpeta, destino_finalizado)
            print(f"📦 Subcarpeta '{subcarpeta}' movida a 'finalizado'. ✅")

print("✅ Todos los PDFs han sido firmados correctamente y las carpetas procesadas fueron movidas a 'finalizado'.")