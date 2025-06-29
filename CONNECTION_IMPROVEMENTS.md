# Connection Handling Improvements

## Problem Addressed

The integration was experiencing connection failures with the error:
```
bleak.exc.BleakError: No backend with an available connection slot that can reach address D8:03:A4:BF:13:34 was found
```

This happens when:
1. The device is not currently connectable
2. All Bluetooth connection slots are busy
3. The device is out of range
4. There are temporary Bluetooth stack issues

## Improvements Made

### 1. Enhanced Connection Validation
- Added `is_device_connectable()` method to check device availability before connection attempts
- Updated `send_move_command()` and `send_stop_command()` to verify connectivity first
- Check for both device presence AND connectability before attempting connections

### 2. Improved Connection Management
- Added proper scanner availability check using `bluetooth.async_get_scanner()`
- Increased connection timeout to 15 seconds (as recommended by HA docs for service resolution)
- Better connection state tracking with `client.is_connected` checks
- Enhanced error handling in disconnect process

### 3. Better Error Handling
- Use `const.LOGGER.exception()` instead of `const.LOGGER.error()` to include tracebacks
- Catch broader exception types including BleakError
- Graceful fallback when connection attempts fail
- Improved warning messages for users

### 4. Device Availability Tracking
- Added `available` property to cover entity based on advertising OR connectivity
- Device shows as available if it's either:
  - Currently advertising (passive monitoring)
  - Currently connectable (for commands)

### 5. Resilient Passive Monitoring
- Status monitoring continues via advertisements even when device isn't connectable
- No connection required for status updates
- Only attempts connections for actual control commands

## Connection Flow

```
User Command → Check Connectable → Verify Scanner → Connect → Send Command → Disconnect
     ↓              ↓                    ↓            ↓          ↓           ↓
   Validate    Pre-validate        Ensure BT       Timeout    Library      Clean
   Device      Connectivity        Available       15s        Command      Disconnect
```

## Benefits

1. **Reduced Connection Failures**: Pre-validation prevents failed connection attempts
2. **Better User Experience**: Clear availability indication in UI
3. **Improved Reliability**: Graceful handling of temporary connectivity issues
4. **Continuous Monitoring**: Status updates work even when commands fail
5. **Resource Efficient**: Only connects when necessary and device is ready

## Error Recovery

- If device becomes unavailable, the cover entity shows as unavailable
- Status monitoring continues via advertisements
- Commands are blocked until device becomes connectable again
- No persistent connection attempts that could exhaust resources

This makes the integration much more robust in real-world scenarios where Bluetooth devices may temporarily become unavailable or when multiple integrations compete for connection slots.
