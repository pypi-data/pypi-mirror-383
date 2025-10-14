import argparse
from .comprecion_descomprecion_zip import comprimir_a_zip, descomprimir_zip

def main():
    parser = argparse.ArgumentParser(
        description="📦 Compresor y descompresor ZIP con progreso visual"
    )
    parser.add_argument("accion", choices=["comprimir", "descomprimir"],
                        help="Acción a realizar: 'comprimir' o 'descomprimir'")
    parser.add_argument("ruta", help="Ruta del archivo o carpeta")

    args = parser.parse_args()

    if args.accion == "comprimir":
        comprimir_a_zip(args.ruta)
    elif args.accion == "descomprimir":
        descomprimir_zip(args.ruta)

if __name__ == "__main__":
    main()
