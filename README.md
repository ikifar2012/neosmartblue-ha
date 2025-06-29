# Neo Smart Blinds Blue Home Assistant Integration

A Home Assistant custom component for controlling Neo Smart Bluetooth blinds.

## 🤖 AI-Generated Integration

This Home Assistant integration was **generated using AI assistance** and is currently **in the process of being cleaned up and refined**. While the core functionality is working, some code may not follow best practices or may contain inefficiencies that are being addressed.

### What's Human-Written vs AI-Generated

- **`neosmartblue.py`** - The core Bluetooth communication library is **entirely human-written** by Matheson Steplock the project maintainer
- **Home Assistant Integration Code** - The custom component files (`__init__.py`, `coordinator.py`, `config_flow.py`, etc.) were **AI-generated** and are being manually reviewed and improved

## 🚧 Current Status

This integration is functional but under active development:

- ✅ **Working**: Device discovery, status monitoring, position control
- 🔄 **In Progress**: Code cleanup, error handling improvements, optimization
- 📋 **Planned**: Better documentation,

## Features

- **Passive Monitoring**: Uses Bluetooth advertisements for status updates (no active polling)
- **Position Control**: Set blind position from 0-100%
- **Stop Command**: Emergency stop functionality
- **Battery Monitoring**: Track device battery levels
- **Connection Management**: Intelligent connection handling with proper cleanup

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Neo Smart Blinds Blue" from HACS
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Neo Smart Blinds Blue" and follow the setup

### Manual Installation

1. Copy the `custom_components/neosmartblue` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI

## Configuration

The integration uses Home Assistant's UI-based configuration flow:

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Neo Smart Blinds Blue"**

## Device Requirements

- Neo Smart Blinds Blue Bluetooth blinds
- Home Assistant with Bluetooth support
- Device must be in pairing/discoverable mode during setup

## Supported Entities

### Cover Entity
- **Position Control**: Set blind position (0-100%)
- **Open/Close**: Standard cover controls
- **Stop**: Emergency stop functionality

### Binary Sensors
- **Charging Status**: Indicates if device is charging
- **Motor Running**: Shows if motor is currently active

### Sensors
- **Battery Level**: Current battery percentage
- **Signal Strength (RSSI)**: Bluetooth signal quality
- **Current Position**: Real-time position feedback

## Technical Details

### Communication Protocol
- **Passive Monitoring**: Uses Bluetooth Low Energy advertisements for status updates
- **Command Mode**: Establishes temporary connections only when sending commands
- **No Polling**: Efficient design that doesn't drain device battery

### Architecture
- **Coordinator Pattern**: Centralized data management with Home Assistant's DataUpdateCoordinator
- **Event-Driven**: Updates triggered by Bluetooth advertisement events
- **Connection Pooling**: Managed connections with proper cleanup and error handling

## Contributing

Since this is an AI-generated integration being cleaned up, contributions are welcome:

1. **Code Review**: Help identify areas for improvement
2. **Testing**: Test with different device configurations
3. **Documentation**: Improve documentation and examples
4. **Bug Reports**: Report issues with detailed logs


## Known Issues

- Some error handling may be overly broad (AI-generated )
- Code structure may not follow all Home Assistant best practices
- Documentation is still being refined


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Core Library**: The `neosmartblue.py` Bluetooth communication library is written by [Matheson Steplock](https://github.com/ikifar2012)
- **Neo Smart Blinds**: Thanks to Neo Smart for providing the API and documentation for their Bluetooth blinds
- **Integration Framework**: Built on Home Assistant's excellent integration APIs
- **AI Assistance**: Integration code generated with AI assistance for rapid prototyping

---

**Note**: This integration is actively being improved. While functional, expect regular updates as the code is refined and optimized. Feedback and contributions are appreciated!
