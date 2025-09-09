# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in TrustWipe, please report it by emailing our security team at security@trustwipe.org (replace with actual email).

**Please do not report security vulnerabilities through public GitHub issues.**

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

We will respond to security reports within 48 hours and provide regular updates on our progress.

## Security Considerations

### Data Wiping Security

- TrustWipe implements industry-standard wiping algorithms
- Multiple pass options available for enhanced security
- Verification mechanisms to ensure complete erasure
- Certificates generated for audit trails

### System Security

- Requires root privileges for disk operations
- Input validation on all user inputs
- Secure handling of system information
- Protection against command injection

### Certificate Security

- Certificates stored with appropriate file permissions
- Cryptographic checksums for verification
- Tamper-evident certificate structure
- Secure certificate directory permissions

## Best Practices

When using TrustWipe:

1. **Always verify target device** before wiping
2. **Use multiple confirmations** for destructive operations
3. **Store certificates securely** for compliance
4. **Keep logs** for audit purposes
5. **Test on non-critical data** first
6. **Use appropriate wiping method** for your security requirements

## Compliance

TrustWipe follows these security standards:

- NIST 800-88 Guidelines for Media Sanitization
- DoD 5220.22-M Data Sanitization Standard
- ISO/IEC 27040:2015 Storage Security
- GDPR data protection requirements
