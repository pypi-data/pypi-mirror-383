import zipfile
import os
from tqdm import tqdm

def _get_folder_size(path):
    """Calcula el tamaño total de una carpeta (en bytes)."""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

def _human_readable_size(size_bytes):
    """Convierte bytes a KB, MB, GB..."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def comprimir_a_zip(ruta_in):
    """Comprime una carpeta en un archivo .zip con barra de progreso."""
    if not os.path.isdir(ruta_in):
        raise ValueError("Debe indicar una carpeta válida para comprimir.")

    ruta_out = ruta_in.rstrip(os.sep) + ".zip"
    total_archivos = sum(len(files) for _, _, files in os.walk(ruta_in))
    tamaño_original = _get_folder_size(ruta_in)

    print(f"📦 Comprimiendo {total_archivos} archivos a '{ruta_out}'.")
    with zipfile.ZipFile(ruta_out, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta, _, archivos in os.walk(ruta_in):
            for archivo in tqdm(archivos, desc="📦 Progreso", unit="archivo"):
                ruta_completa = os.path.join(carpeta, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_in)
                zipf.write(ruta_completa, ruta_relativa)

    tamaño_zip = os.path.getsize(ruta_out)
    ratio = 100 * (1 - (tamaño_zip / tamaño_original)) if tamaño_original > 0 else 0

    print(f"✅ Carpeta comprimida correctamente en: {ruta_out}")
    print(f"📊 Tamaño original: {_human_readable_size(tamaño_original)}")
    print(f"📦 Tamaño comprimido: {_human_readable_size(tamaño_zip)}")
    print(f"💾 Compresión lograda: {ratio:.2f}% de reducción")

    return f"Archivo ZIP creado en {ruta_out}"

def descomprimir_zip(ruta_zip):
    """Descomprime un archivo .zip en una carpeta."""
    if not ruta_zip.lower().endswith('.zip') or not os.path.exists(ruta_zip):
        raise ValueError("Debe indicar un archivo .zip válido.")

    ruta_out = ruta_zip[:-4]
    with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
        nombres = zip_ref.namelist()
        total = len(nombres)
        print(f"📂 Descomprimiendo {total} archivos a '{ruta_out}'.")
        for nombre in tqdm(nombres, desc="📂 Progreso", unit="archivo"):
            zip_ref.extract(nombre, ruta_out)

    print(f"✅ Archivo descomprimido en: {ruta_out}")
    return f"Archivo descomprimido en {ruta_out}"

