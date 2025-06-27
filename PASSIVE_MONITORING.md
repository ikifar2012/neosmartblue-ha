# NeoSmart Blue Integration - Passive Monitoring

This document explains how the NeoSmart Blue Home Assistant integration works with **no active connections**, relying entirely on BLE advertisements for status data.

## How It Works

The integration uses the `neosmartblue.py` library to parse status information from BLE advertisements broadcast by NeoSmart Blue devices. This approach provides several advantages:

### Advantages of Passive Monitoring
- **No connection overhead**: No need to maintain active BLE connections
- **Better battery life**: Devices don't need to keep connections alive
- **Higher reliability**: No connection drops or timeouts
- **Multiple integrations**: Multiple Home Assistant instances can monitor the same device
- **Real-time updates**: Status changes are broadcast immediately

## Status Data Available

The integration extracts the following information from BLE advertisements:

### Core Status
- **Battery Level**: 0-100% charge level
- **Current Position**: 0-100% blind position
- **Target Position**: 0-100% target position
- **RSSI**: Signal strength

### Motor Status
- **Motor Running**: Whether the motor is currently moving
- **Motor Direction**: Up or down movement
- **Charging**: Whether the device is currently charging

### Limit Settings
- **Up Limit Set**: Whether up limit has been configured
- **Down Limit Set**: Whether down limit has been configured
- **Limit Range Size**: Number of motor turns for full range

### Advanced Features
- **Touch Control**: Whether touch control is active
- **Channel Setting Mode**: Device in channel configuration mode
- **Reverse Rotation**: Motor direction is reversed

## Technical Implementation

### Advertisement Parsing
```python
# The integration uses the neosmartblue.py library to parse 5-byte status payloads
from neosmartblue.py import parse_status_data

# Manufacturer ID 2407 is used for NeoSmart devices
manufacturer_data = service_info.manufacturer_data[2407]
status_payload = manufacturer_data[:5]  # First 5 bytes contain status

# Parse into structured data
parsed_status = parse_status_data(status_payload)
```

### Real-time Updates
The coordinator listens for BLE advertisement events and automatically updates entity states:

```python
@callback
def handle_bluetooth_event(self, service_info, change):
    if change == bluetooth.BluetoothChange.ADVERTISEMENT:
        status_data = self._parse_advertisement_data(service_info)
        if status_data:
            self.async_set_updated_data(status_data)
```

## Device Control

While status monitoring is passive, device control still requires active connections:

- **Position Changes**: Connect briefly to send move commands
- **Stop Commands**: Connect briefly to send stop commands
- **Status Requests**: Can optionally connect to request fresh status

The integration automatically manages connections for control operations while keeping status monitoring completely passive.

## Home Assistant Entities

The integration creates the following entities:

### Sensors
- `sensor.{device}_battery_level`: Battery percentage
- `sensor.{device}_position`: Current blind position
- `sensor.{device}_target_position`: Target position (disabled by default)
- `sensor.{device}_signal_strength`: RSSI value
- `sensor.{device}_limit_range`: Limit range size (disabled by default)

### Binary Sensors
- `binary_sensor.{device}_motor_running`: Motor activity
- `binary_sensor.{device}_charging`: Charging status
- `binary_sensor.{device}_touch_control`: Touch control status (disabled by default)
- `binary_sensor.{device}_up_limit_set`: Up limit configured (disabled by default)
- `binary_sensor.{device}_down_limit_set`: Down limit configured (disabled by default)

### Cover
- `cover.{device}_blind`: Main blind control with position, open, close, stop

## Benefits for Users

1. **Instant Updates**: Position and status changes appear immediately in Home Assistant
2. **Battery Efficient**: Devices last longer without constant connections
3. **More Reliable**: No connection issues affecting status updates
4. **Multiple Monitoring**: Can monitor from multiple devices simultaneously
5. **Rich Information**: Access to all device status flags and settings

## Library Integration

This integration leverages the `neosmartblue.py` library which provides:
- Advertisement parsing functions
- Device scanning capabilities  
- Command generation for control operations
- Proper handling of NeoSmart protocol specifics

The library ensures compatibility with the NeoSmart Blue protocol while abstracting the low-level BLE communication details.
