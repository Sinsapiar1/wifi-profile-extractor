# 🚀 Guía de Despliegue - WiFi Profile Extractor

## 📋 Opciones de Despliegue

### 🖥️ **OPCIÓN 1: Aplicación Local Windows (RECOMENDADO)**

```bash
# 1. Clonar repositorio
git clone https://github.com/Sinsapiar1/wifi-profile-extractor.git
cd wifi-profile-extractor

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar (COMO ADMINISTRADOR)
streamlit run src/app.py
```

**⚠️ IMPORTANTE**: Ejecutar como Administrador para acceder a contraseñas WiFi.

---

### 📦 **OPCIÓN 2: Crear Ejecutable Standalone**

```bash
# 1. Instalar PyInstaller
pip install pyinstaller

# 2. Crear ejecutable
python build_executable.py

# 3. El ejecutable estará en: dist/WiFiProfileExtractor.exe
```

**Ventajas:**
- ✅ No necesita Python instalado
- ✅ Fácil distribución
- ✅ Un solo archivo .exe

---

### ☁️ **OPCIÓN 3: Streamlit Cloud (Solo Demo)**

⚠️ **LIMITACIÓN**: No funciona completamente porque:
- Streamlit Cloud usa Linux (no Windows)
- No hay acceso a comandos `netsh`
- No puede extraer perfiles WiFi reales

**Solo para mostrar la interfaz:**
1. Ve a https://share.streamlit.io/
2. Conecta tu repositorio GitHub
3. Selecciona `src/app.py` como archivo principal

---

### 🐳 **OPCIÓN 4: Docker (Windows Container)**

```dockerfile
# Dockerfile
FROM mcr.microsoft.com/windows/servercore:ltsc2022
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "src/app.py"]
```

---

## 🎯 **RECOMENDACIÓN FINAL**

Para tu aplicación WiFi Profile Extractor, te recomiendo:

1. **Desarrollo/Testing**: Ejecutar localmente con `streamlit run src/app.py`
2. **Distribución**: Crear ejecutable con PyInstaller
3. **Demo online**: Streamlit Cloud con datos simulados

¿Cuál opción prefieres que configuremos?