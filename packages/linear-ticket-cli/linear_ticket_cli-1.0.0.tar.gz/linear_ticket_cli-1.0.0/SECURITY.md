# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Security Considerations

### API Token Security

⚠️ **CRITICAL**: Your Linear API token provides access to your Linear workspace. Treat it like a password:

- **Never commit API tokens to version control**
- **Use environment variables** (`LINEAR_API_TOKEN`) instead of hardcoding
- **Rotate tokens regularly** in Linear settings
- **Use minimal required permissions** when creating tokens
- **Store tokens securely** in production environments

### Local Data

This CLI tool caches ticket data locally for performance:
- **Cache is stored temporarily** and contains workspace data
- **No sensitive authentication data** is cached
- **Clear cache regularly** if sharing development machines
- **Cache location**: Current working directory (temporary files)

### Network Security

- All API communication uses **HTTPS with TLS encryption**
- API requests go directly to **Linear's official API endpoints**
- **No third-party intermediaries** are involved
- **Certificate verification** is enabled by default

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue:

### 🚨 For Security Vulnerabilities

**DO NOT** create a public issue for security vulnerabilities.

Instead, please report security vulnerabilities by:

1. **Email**: Send details to [SECURITY_EMAIL] (replace with actual email)
2. **Subject**: Include "SECURITY" in the subject line
3. **Details**: Provide as much information as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fixes (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Regular Updates**: At least weekly until resolution
- **Resolution**: Coordinated disclosure after fix is available

### What to Include

When reporting security issues, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: How the vulnerability could be exploited
- **Steps**: Detailed steps to reproduce
- **Environment**: Python version, OS, CLI version
- **Evidence**: Screenshots, logs, or proof of concept (if safe)

## Security Best Practices for Users

### Development Environment

1. **Use virtual environments** for Python dependencies
2. **Keep dependencies updated** regularly
3. **Don't commit `.env` files** containing tokens
4. **Use separate tokens** for development and production

### Production Usage

1. **Store tokens in secure environment variables**
2. **Use CI/CD secret management** for automation
3. **Rotate API tokens regularly**
4. **Monitor Linear audit logs** for unexpected activity
5. **Limit token permissions** to minimum required scope

### Continuous Integration

When using in CI/CD pipelines:

```yaml
# Good: Use secure environment variables
env:
  LINEAR_API_TOKEN: ${{ secrets.LINEAR_API_TOKEN }}

# Bad: Never hardcode tokens
env:
  LINEAR_API_TOKEN: "lin_api_1234567890"  # ❌ DON'T DO THIS
```

## Security Features

### Built-in Security

- **Environment variable authentication** (no hardcoded secrets)
- **HTTPS-only API communication**
- **Input validation** and sanitization
- **Error handling** that doesn't leak sensitive information
- **No persistent token storage**

### Privacy Protection

- **No telemetry or analytics** data collection
- **No third-party service integration**
- **Local-only data processing**
- **Temporary caching only**

## Vulnerability History

Currently, no security vulnerabilities have been reported or discovered.

## Contact

For security-related questions or concerns:
- **Security issues**: [SECURITY_EMAIL]
- **General questions**: Create a GitHub issue (for non-security topics)
- **Project maintainers**: See CONTRIBUTING.md for contact information

---

Thank you for helping keep Linear Ticket Manager CLI and our users safe! 🔒