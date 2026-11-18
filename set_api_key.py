import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Guardar la clave de Gemini API en el archivo .env"
    )
    parser.add_argument("api_key", help="Clave GEMINI_API_KEY")
    args = parser.parse_args()

    api_key = args.api_key.strip()
    if not api_key:
        parser.error("La API key no puede estar vacía")

    env_path = Path(__file__).resolve().parent / ".env"
    lineas = []

    if env_path.exists():
        lineas = env_path.read_text(encoding="utf-8").splitlines()

    clave_encontrada = False
    nuevas_lineas = []

    for linea in lineas:
        if linea.strip().startswith("GEMINI_API_KEY="):
            nuevas_lineas.append(f"GEMINI_API_KEY={api_key}")
            clave_encontrada = True
        else:
            nuevas_lineas.append(linea)

    if not clave_encontrada:
        nuevas_lineas.append(f"GEMINI_API_KEY={api_key}")

    env_path.write_text(
        "\n".join(nuevas_lineas).rstrip() + "\n",
        encoding="utf-8",
    )

    print(f"Clave guardada en {env_path}")


if __name__ == "__main__":
    main()