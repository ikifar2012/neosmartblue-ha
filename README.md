# Neo Smart Blinds Blue HA Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.6+-blue.svg)](https://www.home-assistant.io)
[![Bluetooth](https://img.shields.io/badge/Bluetooth-BLE-informational.svg)](https://esphome.io/components/bluetooth_proxy.html)

> 🤖 **AI-Generated Integration** - Currently being refined and optimized

Control your Neo Smart Bluetooth blinds through Home Assistant with passive monitoring and efficient battery usage.

## ✨ Features

- 🔋 **Passive Monitoring** - No battery drain on your blinds
- 🎯 **Position Control** - Precise 0-100% positioning
- ⛔ **Emergency Stop** - Instant stop functionality
- 📊 **Real-time Status** - Battery, position, and signal strength
- 🔗 **Smart Connections** - Connects only when needed

## 🚀 Quick Start

### HACS Installation (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ikifar2012&repository=neosmartblue-ha&category=integration)

1. **Add Custom Repository**:
   ```
   https://github.com/ikifar2012/neosmartblue-ha
   ```
2. **Category**: Integration
3. **Install** "Neo Smart Blinds Blue"
4. **Restart** Home Assistant
5. **Add** integration via Settings → Devices & Services

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/ikifar2012/neosmartblue-ha/releases/latest).
2. Copy the `neosmartblue` directory to your Home Assistant's `config/custom_components/` directory:
3. Restart Home Assistant

## 📱 Supported Entities

| Entity Type | Features |
|-------------|----------|
| **Cover** | Position control, Open/Close, Stop |
| **Sensors** | Battery, RSSI, Position |
| **Binary Sensors** | Charging status, Motor running |

## 🔧 Requirements

- Neo Smart Blinds Blue (Bluetooth)
- Home Assistant 2025.6+
- Bluetooth adapter

## 🚧 Development Status

| Component | Status |
|-----------|--------|
| Device Discovery | ✅ Working |
| Position Control | ✅ Working |
| Battery Monitoring | ✅ Working |
| Code Cleanup | 🔄 In Progress |
| Documentation | 🔄 In Progress |

## 🤝 Contributing

[![GitHub Issues](https://img.shields.io/github/issues/ikifar2012/neosmartblue-ha)](https://github.com/ikifar2012/neosmartblue-ha/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/ikifar2012/neosmartblue-ha)](https://github.com/ikifar2012/neosmartblue-ha/pulls)

Help improve this integration:
- 🐛 Report bugs
- 📝 Improve documentation
- 🧪 Test with your devices
- 💻 Code review

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Credits

- **Core Library**: [Matheson Steplock](https://github.com/ikifar2012)
- **Neo Smart Blinds**: API documentation
- **AI Assistance**: Integration code generation

---

<p align="center">
  <a href="https://github.com/ikifar2012/neosmartblue-ha/issues">Report Bug</a> •
  <a href="https://github.com/ikifar2012/neosmartblue-ha/issues">Request Feature</a> •
  <a href="#contributing">Contribute</a>
</p>
