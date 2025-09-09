# Changelog

All notable changes to TrustWipe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-09

### Added
- Initial release of TrustWipe
- GUI interface with Tkinter
- Command-line interface (CLI)
- Multiple wiping algorithms:
  - Zeros (0x00) - fast wiping
  - Random data - secure wiping
  - DoD 5220.22-M - military standard (3 passes)
  - Gutmann method - maximum security (35 passes)
- Real-time progress monitoring
- System information collection
- Device information detection  
- Certificate generation after wiping
- HTML and JSON certificate formats
- Certificate management and viewing
- Automated installation script
- Build system for distribution packages
- Comprehensive test suite
- Security features:
  - Multiple confirmation dialogs
  - Root privilege checking
  - Input validation
  - Error handling and logging
- Documentation:
  - README with usage instructions
  - Security policy
  - License (MIT)
  - Man page generation
- Example scripts for common use cases
- VMware compatibility testing
- Cross-distribution Linux support:
  - Ubuntu/Debian
  - CentOS/RHEL/Fedora
  - Arch Linux
- Certificate storage in persistent locations:
  - `/boot/trustwipe-certificates/` (primary)
  - `/tmp/trustwipe-certificates/` (fallback)
- Professional certificate design with:
  - System verification checksums
  - Compliance badges (NIST, DoD, ISO, GDPR)
  - Tamper-evident structure
  - Print-friendly formatting

### Security
- Implements NIST 800-88 guidelines
- DoD 5220.22-M compliance
- ISO/IEC 27040:2015 storage security standards
- GDPR data protection compliance
- Cryptographic verification with SHA-256
- Secure certificate generation and storage

### Technical Features
- Python 3.6+ compatibility
- Cross-platform Linux support
- Modular architecture with separate backend
- Thread-safe GUI operations
- Emergency stop functionality
- Comprehensive error handling
- Logging system for audit trails
- Package building and distribution system

### Documentation
- Complete API documentation
- Usage examples and tutorials
- Security considerations
- Installation instructions
- Troubleshooting guide
- Compliance information

### Testing
- Unit tests for all major components
- Integration testing for complete workflows
- Mock testing for safe development
- Continuous testing framework
- VMware environment validation

## [Unreleased]

### Planned Features
- Support for additional wiping algorithms
- Network-based certificate management
- Integration with enterprise audit systems
- Advanced scheduling capabilities
- Multi-device batch operations
- Enhanced progress reporting with ETA
- Configuration file support
- Plugin system for custom algorithms
- Internationalization (i18n) support
- Desktop notifications
- System tray integration

### Under Consideration
- Web-based interface
- RESTful API for automation
- Database backend for large-scale deployments
- Remote management capabilities
- Advanced reporting and analytics
- Integration with asset management systems
