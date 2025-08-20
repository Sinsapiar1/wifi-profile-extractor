"""
Script para corregir la instalación del proyecto.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Ejecutar comando con manejo de errores."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado")
            return True
        else:
            print(f"❌ Error en {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def main():
    print("🔧 Corrigiendo configuración del proyecto WiFi Profile Extractor")
    print("=" * 60)
    
    # 1. Limpiar archivos residuales
    print("🧹 Limpiando archivos residuales...")
    for pattern in ["*.egg-info", "build", "dist", "__pycache__"]:
        for path in Path(".").rglob(pattern):
            if path.exists():
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
    print("✅ Limpieza completada")
    
    # 2. Crear archivos __init__.py faltantes
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/utils/__init__.py",
        "src/config/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = Path(init_file)
        init_path.parent.mkdir(parents=True, exist_ok=True)
        if not init_path.exists():
            init_path.write_text('"""Package initialization."""\n')
            print(f"✅ Creado {init_file}")
    
    # 3. Actualizar pip
    run_command("python -m pip install --upgrade pip", "Actualizando pip")
    
    # 4. Instalar dependencias básicas
    basic_deps = ["streamlit", "pandas", "openpyxl"]
    for dep in basic_deps:
        run_command(f"pip install {dep}", f"Instalando {dep}")
    
    print("\n🎉 Configuración corregida!")
    print("📋 Próximos pasos:")
    print("1. Ejecutar: streamlit run src/app.py")
    print("2. Si necesitas herramientas de desarrollo: pip install pytest black flake8")

if __name__ == "__main__":
    main()