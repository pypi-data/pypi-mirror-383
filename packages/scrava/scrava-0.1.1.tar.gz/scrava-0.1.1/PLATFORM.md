# Platform-Specific Installation Guide

This guide helps you install and run Scrava on different platforms and architectures.

## 🍎 macOS

### Apple Silicon (M1/M2/M3/M4) - ARM64

**Recommended Installation:**
```bash
# Use native ARM64 architecture for best performance
arch -arm64 pip3 install scrava

# Or install from source
arch -arm64 pip3 install -e .
```

**Running Scrava:**
```bash
# If you get architecture mismatch errors, use:
arch -arm64 scrava

# Or create an alias in your ~/.zshrc or ~/.bashrc:
alias scrava='arch -arm64 scrava'
```

**Common Issues:**

1. **"mach-o file, but is an incompatible architecture" error:**
   - This means Python or packages were installed with wrong architecture
   - Solution: Reinstall with `arch -arm64` prefix

2. **Mixed x86_64 and arm64 packages:**
   ```bash
   # Clean reinstall
   arch -arm64 pip3 uninstall scrava pydantic pydantic-core
   arch -arm64 pip3 install scrava
   ```

### Intel Mac - x86_64

**Installation:**
```bash
pip3 install scrava
```

**Running Scrava:**
```bash
scrava
```

No special considerations needed for Intel Macs.

---

## 🪟 Windows

### Windows 10/11 (64-bit)

**Installation using Command Prompt:**
```cmd
pip install scrava
```

**Installation using PowerShell:**
```powershell
pip install scrava
```

**Running Scrava:**
```cmd
scrava
```

**Common Issues:**

1. **"scrava is not recognized" error:**
   - Add Python Scripts directory to PATH
   - Usually located at: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts`

2. **SSL Certificate errors:**
   ```cmd
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org scrava
   ```

3. **Permission errors:**
   ```cmd
   # Install for current user only
   pip install --user scrava
   ```

### Windows with WSL (Windows Subsystem for Linux)

Follow the Linux installation instructions below.

---

## 🐧 Linux

### Ubuntu / Debian

**Installation:**
```bash
# Install pip if not available
sudo apt-get update
sudo apt-get install python3-pip

# Install Scrava
pip3 install scrava

# Or use system package manager
sudo pip3 install scrava
```

**Running Scrava:**
```bash
scrava
```

### Fedora / RHEL / CentOS

**Installation:**
```bash
# Install pip if not available
sudo dnf install python3-pip

# Install Scrava
pip3 install scrava
```

### Arch Linux

**Installation:**
```bash
# Install pip if not available
sudo pacman -S python-pip

# Install Scrava
pip install scrava
```

**Common Linux Issues:**

1. **Command not found:**
   ```bash
   # Add to PATH in ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Permission errors:**
   ```bash
   # Install for user only
   pip3 install --user scrava
   ```

---

## 🐳 Docker

Run Scrava in a Docker container for consistent environment across platforms.

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Scrava
RUN pip install --no-cache-dir scrava[all]

# Copy your project
COPY . /app

# Default command
CMD ["scrava", "--help"]
```

**Build and Run:**
```bash
# Build image
docker build -t scrava-app .

# Run
docker run -it scrava-app scrava new my_project
```

---

## 🔧 Virtual Environments

### Using venv (Recommended)

**Create and activate:**

**macOS/Linux:**
```bash
python3 -m venv scrava-env
source scrava-env/bin/activate
pip install scrava
```

**Windows:**
```cmd
python -m venv scrava-env
scrava-env\Scripts\activate
pip install scrava
```

### Using conda

```bash
# Create environment
conda create -n scrava python=3.11
conda activate scrava

# Install Scrava
pip install scrava
```

---

## 🔍 Troubleshooting

### Check Python Architecture (macOS)

```bash
# Check Python architecture
python3 -c "import platform; print(platform.machine())"
# arm64 = Apple Silicon
# x86_64 = Intel
```

### Check Package Architecture (macOS)

```bash
# Check pydantic-core architecture
python3 -c "import pydantic_core; print(pydantic_core.__file__)"
file /path/to/pydantic_core.so
```

### Verify Installation

```bash
# Run version check
scrava version

# This will show:
# - Scrava version
# - Python version
# - Platform information
# - Installed dependencies
```

### Complete Reinstall

**macOS (Apple Silicon):**
```bash
# Uninstall everything
pip3 uninstall -y scrava httpx parsel pydantic pydantic-core structlog typer rich

# Reinstall with correct architecture
arch -arm64 pip3 install scrava
```

**Other Platforms:**
```bash
# Uninstall
pip uninstall -y scrava

# Clear cache
pip cache purge

# Reinstall
pip install scrava
```

---

## 🚀 Performance Tips

### macOS Apple Silicon
- Always use native ARM64 Python for 2-3x better performance
- Avoid Rosetta 2 emulation for production use

### Windows
- Use Windows Terminal for better CLI experience
- Enable ANSI color support in Windows 10+

### Linux
- Use Python 3.9+ for best async performance
- Consider using pypy for CPU-intensive scraping

---

## 📝 Platform-Specific Features

### Browser Support (Playwright)

**macOS:**
```bash
pip install scrava[browser]
playwright install chromium  # Downloads ~300MB
```

**Windows:**
```cmd
pip install scrava[browser]
playwright install chromium
```

**Linux:**
```bash
pip install scrava[browser]
playwright install-deps chromium  # Installs system dependencies
playwright install chromium
```

---

## 🆘 Getting Help

If you encounter platform-specific issues:

1. **Check Scrava version:**
   ```bash
   scrava version
   ```

2. **Verify dependencies:**
   - Lists all installed packages
   - Shows which are missing

3. **Report issues:**
   - GitHub Issues: https://github.com/nextractdevelopers/Scrava/issues
   - Include output from `scrava version`
   - Include your platform: `uname -a` (macOS/Linux) or `systeminfo` (Windows)

---

## ✅ Supported Platforms

| Platform | Architecture | Supported | Notes |
|----------|-------------|-----------|-------|
| macOS | Apple Silicon (ARM64) | ✅ Yes | Use `arch -arm64` prefix |
| macOS | Intel (x86_64) | ✅ Yes | Standard installation |
| Windows | x86_64 | ✅ Yes | Windows 10+ recommended |
| Windows | ARM64 | ⚠️ Limited | Some dependencies may not have wheels |
| Linux | x86_64 | ✅ Yes | All major distros |
| Linux | ARM64 | ✅ Yes | Raspberry Pi, etc. |
| Linux | ARM32 | ⚠️ Limited | May need to build from source |

---

## 📦 Minimal Requirements

- **Python:** 3.8+ (3.11+ recommended)
- **RAM:** 512MB minimum, 2GB+ recommended
- **Disk:** 100MB for Scrava, 500MB+ with browser support
- **Network:** Required for downloading pages

---

**Happy Scraping on Any Platform! 🚀**


