# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

As this is a new project, only the latest version receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do NOT open a public issue**.

### How to Report

1. **Email the maintainer** directly (check the package metadata for contact info)
2. Or open a private security advisory on GitHub: Go to the Security tab → "Report a vulnerability"

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### What to Expect

This project is not actively maintained, so response times may vary. Security issues will be addressed when possible, but there are no guaranteed timelines.

### After Reporting

- If accepted: A fix will be released when time permits, and you'll be credited in the release notes (if you want)
- If declined: We'll explain why we don't consider it a security issue

**Note:** Given the limited maintenance, consider forking the project and applying your own security fixes if you need them urgently. PRs with security fixes are always welcome.

## Security Considerations

This library:
- Handles credentials (basic auth) - ensure you're using HTTPS for your config server
- Loads configuration into environment variables - be careful what you log
- Does not encrypt/decrypt values - rely on Spring Config Server's encryption features
- Fails fast if config server is unreachable - this prevents starting with insecure defaults

**Best practices:**
- Always use HTTPS for your config server URL
- Store credentials in environment variables, not in code
- Don't log the configuration after loading (it may contain secrets)
- Use Spring Config Server's encryption for sensitive values
