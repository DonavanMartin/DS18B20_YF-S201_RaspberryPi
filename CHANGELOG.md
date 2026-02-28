# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-02-27

### Added
- GPIO diagnostic startup test for YF-S201 (3-second GPIO state check at startup)
- Parallel sensor reading for DS18B20 using Python threading (Queue-based architecture)
- Thread worker function `read_temp_threaded()` for concurrent sensor reads
- Enhanced edge detection output with formatted Hz values in debug mode

### Improved
- DS18B20 performance: 6 sensors now read in parallel (~750ms vs sequential 4.5s = 6× speedup)
- `read_ext_temp()` function uses line-by-line parsing with early exit optimization
- YF-S201 sample interval reduced from 10s → 1s for better water flow data granularity
- Fixed-rate sampling using time.time() for accurate microsecond-precision polling
- CPU optimization: YF-S201 reduced loop sleep from 1ms → 100µs
- install.sh now detects modern Raspberry Pi OS boot paths (/boot/firmware/config.txt)
- install.sh prevents duplicate w1-gpio overlay entries with grep check
- install.sh provides better user feedback with [INFO], [ERROR], [SUCCESS] prefixes
- Batch JSON writing: DS18B20 sends all sensor readings in single InfluxDB request
- README.md updated with dual installation methods (automated vs raspi-config manual)

### Fixed
- YF-S201 debug output now includes [FLOW] logger prefixes for consistency
- YF-S201 sample startup state now logged when DEBUG=True
- README.md troubleshooting section now references /boot/firmware/config.txt paths

### Changed
- **BREAKING**: YF-S201 sample_rate changed from 10s → 1s (improves measurement fidelity)

## [2.1.1] - 2026-02-27

### Added
- Sensor-type logging distinction in InfluxDB write confirmations and errors
- `sensor_type` parameter in DBconnection.sendJSON() function for unified logging
- [FLOW] and [TEMP] prefixes in success/error messages from InfluxDB module
- `--debug` command-line argument for both YF-S201 and DS18B20 sensors
- Conditional debug logging in InfluxDB module (success messages only print in debug mode)
- DBconnection.sendJSON() to accept optional `debug` parameter
- InfluxDB success messages now respect debug flag (errors always printed)
- README.md updated with `--debug` usage examples

## [2.1.0] - 2026-02-27

### Added
- InfluxDB systemd timeout configuration for Raspberry Pi Zero stability
- Automatic timeout extension to 300 seconds during service startup

### Improved
- Enhanced install.sh with Pi Zero performance optimization
- Better service initialization reliability on resource-constrained hardware

## [2.0.0] - 2026-02-27

### Added
- Complete English internationalization of all code comments and messages
- Comprehensive README restructuring with troubleshooting guide
- InfluxDB 1.8 documentation and Chronograf UI integration
- Chronograf and Grafana screenshots in documentation
- Line-buffering for real-time console output in sensor scripts
- Deprecation warning fixes (datetime.utcnow() → datetime.now(timezone.utc))
- Resource links section with official documentation
- GPIO pinout tables for both sensors
- Performance optimization guide for Raspberry Pi Zero

### Changed
- License migration from MIT to GPLv3 (derivative works must be published)
- DS18B20 installation: pip3 → python3 -m pip with --break-system-packages flag
- InfluxDB documentation: clarified deprecated UI on port 8083
- Improved code formatting and consistency across Python scripts
- Enhanced service startup documentation (systemd + rc.local)

### Fixed
- Duplicate `import os` in DS18B20/main.py
- Typo: "devives" → "devices"
- Typo: "Celcius" → "Celsius"
- Console logging delay in YF-S201/main.py
- InfluxDB installation script for Raspberry Pi Zero 32-bit compatibility

### Removed
- Manual stdout.flush() calls (replaced with line-buffering)

## [1.0.0] - 2019-01-01

### Added
- Initial project setup with DS18B20 and YF-S201 sensor support
- InfluxDB integration for time-series data storage
- Grafana dashboarding and visualization
- Chronograf UI for InfluxDB management
- PiOLED optional display support
- Basic installation scripts for all components
