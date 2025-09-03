# <img src="../meowdown-web/public/maoer.png" width="39" height="39" alt="Meowdown Logo" style="vertical-align: middle;">   Meowdown · MdImgConverter

¡Convierte imágenes de Markdown a formato WebP y súbelas a servicios de alojamiento de imágenes con un clic! (=^･ω･^=)✧

![Preview](../icons/image/preview.png)

---

## 💫 Características

### 🌟 Funciones Principales
- 🐾 **Conversión de Un Clic**: Detecta automáticamente imágenes de Markdown y las convierte a formato WebP
- 🎚️ **Calidad Ajustable**: Controla el balance calidad/tamaño con deslizador, por defecto 73% óptimo
- 🔗 **Reescritura de Rutas**: Reemplazo inteligente de enlaces `images/*.webp` o URL externas
- ☁️ **Subida a Alojamiento de Imágenes**: Soporte para Alibaba Cloud OSS, Tencent Cloud COS, Qiniu Cloud, S3, GitHub y otros servicios

### 🚀 Versiones de Aplicación
- 🖥️ **Versión de Escritorio**: Construida con Tauri, tamaño compacto, excelente rendimiento, experiencia nativa
- 🌐 **Versión Web**: React moderno + Chakra UI, soporta uso en línea
- 🪄 **Interfaz Limpia**: Eliminados botones de depuración y configuración de backend, enfocado en funcionalidad principal

---

## 🚀 Inicio Rápido

### 🖥️ Aplicación de Escritorio (Recomendada)
- Ve a la página de Releases del repositorio y descarga la última versión de escritorio:
  - 📦 **Instalador MSI**: `Meowdown_0.1.0_x64_en-US.msi` - Instalador estándar de Windows
  - 🚀 **Versión Portable**: `Meowdown_0.1.0_x64-setup.exe` - Ejecuta directamente sin instalación
- Si es bloqueado por SmartScreen en la primera ejecución, haz clic en "Más información" → "Ejecutar de todas formas"
- ¡Construido con Tauri, tamaño compacto y excelente rendimiento! ✨

### 🌐 Aplicación Web
- Experiencia en línea: Visita la versión Web desplegada
- Requiere servicio backend: `python meowdown-backend/main.py`
- Adecuado para despliegue en servidor o desarrollo local

### 👨‍💻 Versión de Desarrollador
- ¿Quieres ejecutar desde el código fuente? Ver `Read.md/coder-README.md`
- Desarrollo de escritorio: `cd desktop && npm run tauri dev`
- Desarrollo web: `cd meowdown-web && npm run dev`

---

## 🎯 Uso

### 🖥️ Uso de Escritorio
1. 📝 **Entrada de Contenido**: Pega o arrastra archivos Markdown al editor
2. 🎚️ **Ajustar Calidad**: Usa el deslizador derecho para ajustar la calidad de compresión (por defecto 73% está genial)
3. 🔄 **Iniciar Conversión**: Haz clic en el botón "Iniciar Conversión"
4. ☁️ **Subir a Alojamiento de Imágenes**: ¿Necesitas enlaces externos? Haz clic en "Configuración" para configurar el alojamiento de imágenes para subida automática
5. 💾 **Guardar Resultados**: Guarda el nuevo archivo Markdown después de la conversión

### 🌐 Uso Web
1. 🚀 Iniciar backend: `python meowdown-backend/main.py`
2. 🌐 Abrir interfaz Web (usualmente `http://localhost:8000`)
3. 📝 Ingresa contenido Markdown en el editor izquierdo
4. 🎛️ Ajusta parámetros en la derecha y haz clic en convertir
5. 📥 Descarga el archivo convertido

---

## 🧰 Servicios de Alojamiento de Imágenes Soportados

### 📡 Alibaba Cloud OSS
**Parámetros de Configuración:**
- **Access Key ID** y **Access Key Secret**: Claves de cuenta de Alibaba Cloud
- **Bucket**: Nombre del bucket de almacenamiento
- **Endpoint**: ej., `oss-cn-beijing` (completa automáticamente protocolo y dominio)
- **Dominio Personalizado**: Opcional, dominio CDN vinculado
- **Prefijo de Ruta de Almacenamiento**: Opcional, ej., `images/` crea estructura de directorio en bucket

**Formato de URL:** `https://bucket.oss-cn-beijing.aliyuncs.com/path/file.webp`

### 🌪️ Tencent Cloud COS
**Parámetros de Configuración:**
- **Secret ID** y **Secret Key**: Claves de cuenta de Tencent Cloud
- **Bucket**: Nombre del bucket de almacenamiento (formato: `bucket-appid`)
- **Region**: Región, ej., `ap-beijing`
- **Dominio Personalizado**: Opcional, dominio CDN vinculado
- **Prefijo de Ruta de Almacenamiento**: Opcional, prefijo de directorio

**Formato de URL:** `https://bucket-appid.cos.ap-beijing.myqcloud.com/path/file.webp`

### 🦄 Qiniu Cloud Kodo
**Parámetros de Configuración:**
- **Access Key** y **Secret Key**: Claves de cuenta de Qiniu Cloud
- **Bucket**: Nombre del espacio de almacenamiento
- **Domain**: Dominio de acceso vinculado (requerido)
- **Prefijo de Ruta de Almacenamiento**: Opcional, prefijo de directorio

**Formato de URL:** `https://your-domain.com/path/file.webp`

### 🪣 Almacenamiento Compatible con S3
**Servicios Soportados:** AWS S3, MinIO, Alibaba Cloud OSS S3 API, Tencent Cloud COS S3 API, etc.
**Parámetros de Configuración:**
- **Access Key** y **Secret Key**: Claves de acceso S3
- **Bucket**: Nombre del bucket de almacenamiento
- **Region**: Región, ej., `us-east-1`
- **Endpoint**: Opcional, endpoint personalizado (ej., dirección del servidor MinIO)
- **Dominio Personalizado**: Opcional, dominio CDN
- **Prefijo de Ruta de Almacenamiento**: Opcional, prefijo de directorio
- **Estilo de Ruta**: Opcional, habilitar acceso de estilo de ruta

**Formato de URL:** `https://s3.region.amazonaws.com/bucket/path/file.webp`

### 🐙 Repositorio GitHub
**Parámetros de Configuración:**
- **Personal Access Token**: Token de acceso personal de GitHub (requiere permisos de repo)
- **Repository Owner**: Nombre de usuario u organización de GitHub
- **Repository Name**: Nombre del repositorio para almacenar imágenes
- **Branch**: Rama objetivo, ej., `main` o `master`
- **Prefijo de Ruta del Repositorio**: Opcional, ej., `images/` crea directorio en repositorio
- **Dominio Personalizado**: Opcional, acceso por dominio personalizado
- **Usar jsDelivr CDN**: Opcional, acceso acelerado vía CDN

**Formato de URL:**
- Enlace directo GitHub: `https://raw.githubusercontent.com/user/repo/branch/path/file.webp`
- jsDelivr CDN: `https://cdn.jsdelivr.net/gh/user/repo@branch/path/file.webp`

## 🔧 Consejos de Configuración
- **Endpoint de Alibaba Cloud OSS**: `oss-cn-beijing` → se convierte automáticamente en `https://oss-cn-beijing.aliyuncs.com`
- **Protocolo de URL**: Todos los servicios soportan HTTPS (recomendado) y HTTP
- **Limpiar Configuración**: Haz clic en el botón "Limpiar" en el diálogo de configuración de alojamiento de imágenes
- **Probar Subida**: Haz clic en "Probar Subida" después de la configuración para verificar que los ajustes son correctos

---

## 🌍 Soporte Multi-idioma
La aplicación ahora soporta múltiples idiomas:
- 🇨🇳 **Chino** (Por defecto)
- 🇺🇸 **Inglés**
- 🇪🇸 **Español**
- 🇫🇷 **Francés**

Puedes cambiar idiomas usando el selector de idioma en la esquina superior derecha de la interfaz.

---

## 🧭 Hoja de Ruta de Desarrollo
- ✅ **Optimización de Interfaz**: Eliminados botones de depuración y configuración de backend para interfaz más limpia
- ✅ **Versión de Escritorio**: Aplicación de escritorio moderna basada en Tauri completada
- ✅ **Versión Web**: Interfaz moderna React + Chakra UI
- ✅ **Soporte Multi-idioma**: Chino, Inglés, Español, Francés
- 🔄 **Agregar Animaciones de UI**
- 🔄 **Soporte para Otros Formatos de Compresión** (AVIF, JPEG XL)
- 🔄 **Agregar Vista Previa de Renderizado de Archivos Markdown**
- 🔄 **Modo de Procesamiento por Lotes**

---

## 📝 Licencia
MIT. Bienvenido desarrollo secundario y creaciones de fans (por favor mantén la atribución miau).

---

## 📚 Navegación de Documentación

### 🎯 Documentación de Usuario
- **[README.md](../README.md)** - Página principal del proyecto, guía de inicio rápido
- **[README-en.md](README-en.md)** - Documentación en versión inglesa
- **[README-es.md](README-es.md)** - Documentación en versión española
- **[README-fr.md](README-fr.md)** - Documentación en versión francesa
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Guía detallada de construcción y empaquetado
- **[PACKAGING_COMPARISON.md](PACKAGING_COMPARISON.md)** - Comparación de configuración de empaquetado

### 🔧 Documentación de Desarrollador
- **[coder-README.md](coder-README.md)** - Documentación técnica, configuración de entorno de desarrollo
- **[coder-picgo-README.md](coder-picgo-README.md)** - Guía de desarrollo de extensión de alojamiento de imágenes
- **[imd-README.md](imd-README.md)** - Documentación detallada de la biblioteca central imarkdown
- **[imd-README_zh.md](imd-README_zh.md)** - Documentación china de imarkdown

### 🎨 Recursos de Diseño
- **[ICON_MANIFEST.md](ICON_MANIFEST.md)** - Lista de verificación de uso de iconos e instrucciones de configuración
- **[../icons/README.md](../icons/README.md)** - Instrucciones detalladas del paquete de iconos multiplataforma

### 📊 Gestión de Proyecto
- **[meum-README.md](meum-README.md)** - Descripción completa de la estructura de directorios del proyecto
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Índice de documentación y navegación

### 🧪 Documentación de Pruebas
- **[../md-converter-gui/test_images.md](../md-converter-gui/test_images.md)** - Casos de prueba de GUI

---

**Navegación Rápida:**
- 🚀 ¿Quieres usar rápidamente? Ver [README.md](../README.md)
- 🔧 ¿Quieres desarrollar extensiones? Ver [coder-README.md](coder-README.md)
- 📦 ¿Quieres empaquetar tú mismo? Ver [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 🎨 ¿Quieres entender iconos? Ver [ICON_MANIFEST.md](ICON_MANIFEST.md)
- 📁 ¿Quieres entender estructura? Ver [meum-README.md](meum-README.md)

