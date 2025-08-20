import sys
from pathlib import Path

# Asegura que el proyecto raíz esté en sys.path para poder importar el paquete 'src'
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.app import main


if __name__ == "__main__":
    main()

