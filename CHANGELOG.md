# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
