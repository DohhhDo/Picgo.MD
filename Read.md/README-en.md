# <img src="../meowdown-web/public/maoer.png" width="39" height="39" alt="Meowdown Logo" style="vertical-align: middle;">   Meowdown · MdImgConverter

Convert Markdown images to WebP format and upload to image hosting services with one click! (=^･ω･^=)✧

![Preview](../icons/image/preview.png)

---

## 💫 Features

### 🌟 Core Functions
- 🐾 **One-Click Conversion**: Automatically detect Markdown images and convert to WebP format
- 🎚️ **Adjustable Quality**: Control quality/size balance with slider, default 73% optimal
- 🔗 **Path Rewriting**: Smart replacement of `images/*.webp` or external URL links
- ☁️ **Image Hosting Upload**: Support for Alibaba Cloud OSS, Tencent Cloud COS, Qiniu Cloud, S3, GitHub and other image hosting services

### 🚀 Application Versions
- 🖥️ **Desktop Version**: Built with Tauri, compact size, excellent performance, native experience
- 🌐 **Web Version**: Modern React + Chakra UI, supports online usage
- 🪄 **Clean Interface**: Removed debug and backend settings buttons, focused on core functionality

---

## 🚀 Quick Start

### 🖥️ Desktop Application (Recommended)
- Go to the repository's Releases page and download the latest desktop version:
  - 📦 **MSI Installer**: `Meowdown_0.1.0_x64_en-US.msi` - Standard Windows installer
  - 🚀 **Portable Version**: `Meowdown_0.1.0_x64-setup.exe` - Run directly without installation
- If blocked by SmartScreen on first run, click "More info" → "Run anyway"
- Built with Tauri, compact size and excellent performance! ✨

### 🌐 Web Application
- Online experience: Visit the deployed Web version
- Requires backend service: `python meowdown-backend/main.py`
- Suitable for server deployment or local development

### 👨‍💻 Developer Version
- Want to run from source? See `Read.md/coder-README.md`
- Desktop development: `cd desktop && npm run tauri dev`
- Web development: `cd meowdown-web && npm run dev`

---

## 🎯 Usage

### 🖥️ Desktop Usage
1. 📝 **Input Content**: Paste or drag Markdown files to the editor
2. 🎚️ **Adjust Quality**: Use the right slider to adjust compression quality (default 73% is great)
3. 🔄 **Start Conversion**: Click the "Start Conversion" button
4. ☁️ **Upload to Image Hosting**: Need external links? Click "Settings" to configure image hosting for automatic upload
5. 💾 **Save Results**: Save the new Markdown file after conversion

### 🌐 Web Usage
1. 🚀 Start backend: `python meowdown-backend/main.py`
2. 🌐 Open Web interface (usually `http://localhost:8000`)
3. 📝 Input Markdown content in the left editor
4. 🎛️ Adjust parameters on the right and click convert
5. 📥 Download the converted file

---

## 🧰 Supported Image Hosting Services

### 📡 Alibaba Cloud OSS
**Configuration Parameters:**
- **Access Key ID** and **Access Key Secret**: Alibaba Cloud account keys
- **Bucket**: Storage bucket name
- **Endpoint**: e.g., `oss-cn-beijing` (automatically completes protocol and domain)
- **Custom Domain**: Optional, bound CDN domain
- **Storage Path Prefix**: Optional, e.g., `images/` creates directory structure in bucket

**URL Format:** `https://bucket.oss-cn-beijing.aliyuncs.com/path/file.webp`

### 🌪️ Tencent Cloud COS
**Configuration Parameters:**
- **Secret ID** and **Secret Key**: Tencent Cloud account keys
- **Bucket**: Storage bucket name (format: `bucket-appid`)
- **Region**: Region, e.g., `ap-beijing`
- **Custom Domain**: Optional, bound CDN domain
- **Storage Path Prefix**: Optional, directory prefix

**URL Format:** `https://bucket-appid.cos.ap-beijing.myqcloud.com/path/file.webp`

### 🦄 Qiniu Cloud Kodo
**Configuration Parameters:**
- **Access Key** and **Secret Key**: Qiniu Cloud account keys
- **Bucket**: Storage space name
- **Domain**: Bound access domain (required)
- **Storage Path Prefix**: Optional, directory prefix

**URL Format:** `https://your-domain.com/path/file.webp`

### 🪣 S3 Compatible Storage
**Supported Services:** AWS S3, MinIO, Alibaba Cloud OSS S3 API, Tencent Cloud COS S3 API, etc.
**Configuration Parameters:**
- **Access Key** and **Secret Key**: S3 access keys
- **Bucket**: Storage bucket name
- **Region**: Region, e.g., `us-east-1`
- **Endpoint**: Optional, custom endpoint (e.g., MinIO server address)
- **Custom Domain**: Optional, CDN domain
- **Storage Path Prefix**: Optional, directory prefix
- **Path Style**: Optional, enable path-style access

**URL Format:** `https://s3.region.amazonaws.com/bucket/path/file.webp`

### 🐙 GitHub Repository
**Configuration Parameters:**
- **Personal Access Token**: GitHub personal access token (requires repo permissions)
- **Repository Owner**: GitHub username or organization name
- **Repository Name**: Repository name for storing images
- **Branch**: Target branch, e.g., `main` or `master`
- **Repository Path Prefix**: Optional, e.g., `images/` creates directory in repository
- **Custom Domain**: Optional, custom domain access
- **Use jsDelivr CDN**: Optional, accelerated access via CDN

**URL Format:**
- GitHub direct link: `https://raw.githubusercontent.com/user/repo/branch/path/file.webp`
- jsDelivr CDN: `https://cdn.jsdelivr.net/gh/user/repo@branch/path/file.webp`

## 🔧 Configuration Tips
- **Alibaba Cloud OSS Endpoint**: `oss-cn-beijing` → automatically becomes `https://oss-cn-beijing.aliyuncs.com`
- **URL Protocol**: All services support HTTPS (recommended) and HTTP
- **Clear Configuration**: Click the "Clear" button in the image hosting settings dialog
- **Test Upload**: Click "Test Upload" after configuration to verify settings are correct

---

## 🌍 Multi-language Support
The application now supports multiple languages:
- 🇨🇳 **Chinese** (Default)
- 🇺🇸 **English**
- 🇪🇸 **Spanish**
- 🇫🇷 **French**

You can switch languages using the language selector in the top-right corner of the interface.

---

## 🧭 Development Roadmap
- ✅ **Interface Optimization**: Removed debug and backend settings buttons for cleaner interface
- ✅ **Desktop Version**: Modern desktop application based on Tauri completed
- ✅ **Web Version**: Modern React + Chakra UI interface
- ✅ **Multi-language Support**: Chinese, English, Spanish, French
- 🔄 **Add UI Animations**
- 🔄 **Support for Other Compression Formats** (AVIF, JPEG XL)
- 🔄 **Add Markdown File Rendering Preview**
- 🔄 **Batch Processing Mode**

---

## 📝 License
MIT. Welcome secondary development and fan creations (please retain attribution meow).

---

## 📚 Documentation Navigation

### 🎯 User Documentation
- **[README.md](../README.md)** - Project homepage, quick start guide
- **[README-en.md](README-en.md)** - English version documentation
- **[README-es.md](README-es.md)** - Spanish version documentation
- **[README-fr.md](README-fr.md)** - French version documentation
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Detailed build and packaging guide
- **[PACKAGING_COMPARISON.md](PACKAGING_COMPARISON.md)** - Packaging configuration comparison

### 🔧 Developer Documentation
- **[coder-README.md](coder-README.md)** - Technical documentation, development environment setup
- **[coder-picgo-README.md](coder-picgo-README.md)** - Image hosting extension development guide
- **[imd-README.md](imd-README.md)** - imarkdown core library detailed documentation
- **[imd-README_zh.md](imd-README_zh.md)** - imarkdown Chinese documentation

### 🎨 Design Resources
- **[ICON_MANIFEST.md](ICON_MANIFEST.md)** - Icon usage checklist and configuration instructions
- **[../icons/README.md](../icons/README.md)** - Multi-platform icon pack detailed instructions

### 📊 Project Management
- **[meum-README.md](meum-README.md)** - Complete project directory structure description
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Documentation index and navigation

### 🧪 Test Documentation
- **[../md-converter-gui/test_images.md](../md-converter-gui/test_images.md)** - GUI test cases

---

**Quick Navigation:**
- 🚀 Want to use quickly? See [README.md](../README.md)
- 🔧 Want to develop extensions? See [coder-README.md](coder-README.md)
- 📦 Want to package yourself? See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 🎨 Want to understand icons? See [ICON_MANIFEST.md](ICON_MANIFEST.md)
- 📁 Want to understand structure? See [meum-README.md](meum-README.md)

