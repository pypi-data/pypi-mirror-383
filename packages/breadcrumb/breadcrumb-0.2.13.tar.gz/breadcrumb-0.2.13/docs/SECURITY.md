# Breadcrumb AI Tracer - Security Documentation

This document describes Breadcrumb's security features, data privacy practices, and best practices for secure usage.

## Table of Contents

- [Secret Redaction](#secret-redaction)
- [Data Privacy](#data-privacy)
- [Production Best Practices](#production-best-practices)
- [Database Security](#database-security)
- [Configuration Security](#configuration-security)
- [Threat Model](#threat-model)
- [Responsible Disclosure](#responsible-disclosure)
- [Security Roadmap](#security-roadmap)

---

## Secret Redaction

Breadcrumb automatically redacts sensitive information before storing trace data. This prevents accidental logging of passwords, API keys, tokens, and other secrets.

### Automatic Detection

Breadcrumb uses two complementary detection strategies:

#### 1. Key-Based Redaction

Sensitive data is detected by dictionary key names (case-insensitive):

**Password patterns:**
- `password`, `passwd`, `pwd`, `pass`
- `secret`, `password_hash`, `password_digest`

**API key and token patterns:**
- `api_key`, `apikey`, `api-key`
- `token`, `auth_token`, `access_token`, `refresh_token`
- `secret_key`, `private_key`
- `bearer`, `authorization`, `auth`

**Authentication patterns:**
- `credentials`, `credential`
- `client_secret`, `session_key`, `session_token`

**Security tokens:**
- `security_token`, `csrf_token`, `xsrf_token`

**Cloud provider patterns:**
- `aws_secret`, `aws_secret_access_key`
- `azure_secret`, `gcp_secret`

#### 2. Value-Based Redaction

Sensitive data is also detected by analyzing string values:

**Credit card numbers:**
- Pattern: 16 digits with optional dashes/spaces
- Example: `4532-1234-5678-9010` → `[REDACTED]`

**Social Security Numbers (SSN):**
- Pattern: XXX-XX-XXXX format
- Example: `123-45-6789` → `[REDACTED]`

**JWT tokens:**
- Pattern: Starts with `eyJ` (base64 encoded JSON header)
- Format: `header.payload.signature`
- Example: `eyJhbGc...` → `[REDACTED]`

**AWS access keys:**
- Pattern: Starts with `AKIA` followed by 16 characters
- Example: `AKIAIOSFODNN7EXAMPLE` → `[REDACTED]`

**GitHub tokens:**
- Pattern: Starts with `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- Example: `ghp_1234567890abcdef` → `[REDACTED]`

**Generic API keys:**
- Pattern: Long alphanumeric strings (32+ characters)
- Must contain both letters and numbers (high entropy)

### How It Works

**Before storage:**

```python
# Input data
data = {
    "username": "alice",
    "password": "secret123",
    "api_key": "sk-1234567890",
    "email": "alice@example.com"
}

# Stored data (after redaction)
{
    "username": "alice",
    "password": "[REDACTED]",
    "api_key": "[REDACTED]",
    "email": "alice@example.com"
}
```

**Nested structures:**

```python
# Input
data = {
    "user": {
        "name": "alice",
        "credentials": {
            "password": "secret123",
            "api_key": "sk-1234567890"
        }
    }
}

# Stored (all nested secrets redacted)
{
    "user": {
        "name": "alice",
        "credentials": {
            "password": "[REDACTED]",
            "api_key": "[REDACTED]"
        }
    }
}
```

### Configuration

#### Custom Patterns

Add custom patterns to match your application's secret naming conventions:

```python
from breadcrumb.capture.secret_redactor import configure_redactor

# Add custom patterns
configure_redactor(custom_patterns=[
    'my_secret_*',        # Wildcard patterns
    'internal_token',     # Exact matches
    'app_password'
])

# Now these keys will be redacted
data = {"my_secret_key": "abc123"}  # → {"my_secret_key": "[REDACTED]"}
```

#### Disable Specific Detection

You can disable specific value-based detection types:

```python
configure_redactor(
    redact_credit_cards=False,  # Don't redact credit card patterns
    redact_ssns=True,           # Redact SSNs (default)
    redact_jwts=True,           # Redact JWTs (default)
    redact_api_keys=True        # Redact API keys (default)
)
```

#### Custom Redactor Instance

For advanced use cases, create your own redactor:

```python
from breadcrumb.capture.secret_redactor import SecretRedactor

# Custom redactor with only password patterns
redactor = SecretRedactor(
    key_patterns=['password', 'passwd', 'secret'],
    custom_patterns=['my_app_token'],
    redact_credit_cards=False,
    redact_api_keys=False
)

# Use it
data = {"password": "secret123", "token": "abc"}
redacted = redactor.redact(data)
```

### Limitations

**What is NOT redacted:**

1. **Short strings** (< 8 characters): Too short to be meaningful secrets
2. **Non-string values**: Numbers, booleans are never redacted
3. **Obfuscated secrets**: If secrets are already encoded/encrypted
4. **Variable names**: Only values are redacted, not keys
5. **Code content**: Source code itself is not scanned

**False positives:**

The redactor is conservative and may occasionally redact non-sensitive data if it matches patterns. This is by design - better safe than sorry.

**Example:**
```python
# May be redacted (looks like credit card)
data = {"test_number": "1234-5678-9012-3456"}
# Result: {"test_number": "[REDACTED]"}
```

To avoid false positives, use more specific key names:
```python
data = {"test_card_last_four": "3456"}  # Won't be redacted (only 4 digits)
```

---

## Data Privacy

### What Data is Captured

Breadcrumb captures the following execution data:

**Trace metadata:**
- Trace ID (UUID)
- Start and end timestamps
- Execution status (success/failed/running)
- Duration in milliseconds

**Function call events:**
- Function name and module
- File path and line number
- Timestamp
- Arguments (redacted)
- Return values (redacted)
- Local variables (optional, disabled by default)

**Exception events:**
- Exception type and message
- Stack trace
- File path and line number
- Timestamp

**NOT captured:**
- Network requests/responses (unless explicitly in function args)
- File contents
- Environment variables (unless explicitly in function args)
- System information

### Where Data is Stored

**Local storage only:**
- Breadcrumb stores all data in a local DuckDB database
- Default location: `.breadcrumb/traces.duckdb` in your project directory
- No data is sent to external servers
- No telemetry or analytics

**Database file:**
- SQLite-compatible format (DuckDB)
- Readable by standard tools
- No encryption by default (see Database Security below)

### Data Retention

**Automatic cleanup:**

Breadcrumb supports automatic data retention policies:

```python
from breadcrumb.storage.retention import cleanup_old_traces

# Delete traces older than 30 days
cleanup_old_traces(days=30)

# Delete traces older than 7 days
cleanup_old_traces(days=7)

# Custom database path
cleanup_old_traces(days=30, db_path="/custom/path/traces.duckdb")
```

**Manual cleanup:**

```python
import duckdb

conn = duckdb.connect('.breadcrumb/traces.duckdb')

# Delete all traces
conn.execute("DELETE FROM traces")
conn.execute("DELETE FROM trace_events")
conn.execute("DELETE FROM exceptions")

conn.close()
```

Or simply delete the database file:

```bash
rm .breadcrumb/traces.duckdb
```

### Data Access Control

**File permissions:**

The database file inherits the permissions of your project directory. By default, it's readable by the user who created it.

**Recommended:**

```bash
# Restrict database to owner only
chmod 600 .breadcrumb/traces.duckdb
chmod 700 .breadcrumb/

# Verify permissions
ls -la .breadcrumb/
```

**Multi-user systems:**

On shared systems, ensure `.breadcrumb/` is not world-readable:

```bash
# In your project directory
mkdir -p .breadcrumb
chmod 700 .breadcrumb
```

---

## Production Best Practices

### 1. Selective Instrumentation

**Don't trace everything.** Use selective instrumentation to limit what gets traced:

```python
import breadcrumb

# Only trace application code (include-only workflow)
breadcrumb.init(
    include=["src/**/*.py", "app/**/*.py"],
)
```

**Benefits:**
- Reduces performance overhead
- Minimizes sensitive data exposure
- Keeps database size manageable

### 2. Sampling

Use sampling to trace a subset of requests:

```python
# Trace 10% of requests
breadcrumb.init(sample_rate=0.1)

# Trace 50% of requests
breadcrumb.init(sample_rate=0.5)
```

**When to sample:**
- High-traffic production systems
- Performance-critical code paths
- When database size is a concern

### 3. Review Redaction Patterns

**Before deploying to production:**

1. Review default redaction patterns
2. Add application-specific patterns
3. Test with sample data

```python
from breadcrumb.capture.secret_redactor import configure_redactor

configure_redactor(custom_patterns=[
    'internal_api_key',
    'session_id',
    'oauth_token',
    'refresh_code'
])
```

4. Verify redaction works:

```python
from breadcrumb.capture.secret_redactor import redact_secrets

# Test with sample data
test_data = {
    "user_id": "123",
    "internal_api_key": "should_be_redacted",
    "email": "user@example.com"
}

result = redact_secrets(test_data)
print(result)
# Should show: {"user_id": "123", "internal_api_key": "[REDACTED]", "email": "user@example.com"}
```

### 4. Disable Tracing in Production (Optional)

For maximum security, disable tracing in production and only enable it when debugging:

```python
import os
import breadcrumb

# Only enable in development
is_dev = os.getenv("ENVIRONMENT") == "development"

breadcrumb.init(enabled=is_dev)
```

Or use environment variable:

```bash
# Development
export BREADCRUMB_ENABLED=true

# Production
export BREADCRUMB_ENABLED=false
```

### 5. Secure Database Location

**Don't commit database to version control:**

Add to `.gitignore`:

```
.breadcrumb/
*.duckdb
```

**Use secure location in production:**

```python
breadcrumb.init(db_path="/var/secure/traces.duckdb")
```

Ensure the directory has restricted permissions:

```bash
mkdir -p /var/secure
chmod 700 /var/secure
chown your-app-user:your-app-group /var/secure
```

### 6. Regular Cleanup

Implement automatic cleanup:

```python
from breadcrumb.storage.retention import cleanup_old_traces
import schedule

# Clean up traces older than 7 days, every day at 2 AM
def cleanup_job():
    cleanup_old_traces(days=7)
    print("Cleanup completed")

schedule.every().day.at("02:00").do(cleanup_job)
```

Or use a cron job:

```bash
# crontab -e
0 2 * * * python -c "from breadcrumb.storage.retention import cleanup_old_traces; cleanup_old_traces(days=7)"
```

### 7. Monitor Database Size

Keep track of database size:

```bash
# Check database size
du -h .breadcrumb/traces.duckdb

# Alert if > 1GB
SIZE=$(du -m .breadcrumb/traces.duckdb | cut -f1)
if [ $SIZE -gt 1024 ]; then
    echo "WARNING: Database exceeds 1GB"
fi
```

---

## Database Security

### Encryption at Rest

**DuckDB does not support encryption by default.** For sensitive data, consider:

#### Option 1: Filesystem Encryption

Use encrypted filesystem (Linux):

```bash
# LUKS encryption
cryptsetup luksFormat /dev/sdX
cryptsetup open /dev/sdX breadcrumb-data
mkfs.ext4 /dev/mapper/breadcrumb-data
mount /dev/mapper/breadcrumb-data /mnt/secure
```

Store database in encrypted mount:

```python
breadcrumb.init(db_path="/mnt/secure/traces.duckdb")
```

#### Option 2: Application-Level Encryption

Encrypt sensitive fields before storing:

```python
from cryptography.fernet import Fernet

# Generate key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt before tracing
def process_payment(card_number):
    encrypted_card = cipher.encrypt(card_number.encode())
    # Now trace with encrypted data
    ...
```

#### Option 3: Use In-Memory Backend

For temporary tracing without persistence:

```python
breadcrumb.init(backend="memory")
```

Data is only kept in RAM and never written to disk.

### Access Control

**Restrict database access:**

```bash
# Only owner can read/write
chmod 600 .breadcrumb/traces.duckdb

# Verify
ls -l .breadcrumb/traces.duckdb
# Should show: -rw------- 1 user user ...
```

**Multi-user environments:**

Create a dedicated user:

```bash
# Create breadcrumb user
useradd -r -s /bin/false breadcrumb

# Set ownership
chown breadcrumb:breadcrumb .breadcrumb/traces.duckdb
```

Run application as breadcrumb user:

```bash
sudo -u breadcrumb python app.py
```

### Network Isolation

**MCP server runs on stdio by default** - no network exposure.

For future TCP transport support, use firewall rules:

```bash
# Allow only localhost
iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

---

## Configuration Security

### Environment Variables

**Avoid exposing secrets in environment variables:**

```bash
# BAD: Secret in environment variable
export API_KEY="sk-1234567890"

# GOOD: Load from secure file
export API_KEY_FILE="/secure/api-key.txt"
```

**Breadcrumb environment variables:**

These are safe (no secrets):

```bash
export BREADCRUMB_ENABLED=true
export BREADCRUMB_DB_PATH=".breadcrumb/traces.duckdb"
export BREADCRUMB_SAMPLE_RATE=0.5
```

### Configuration Files

**Don't commit configuration with secrets:**

```python
# BAD
breadcrumb.init(
    db_path="s3://my-bucket/traces.duckdb",
    aws_key="AKIAIOSFODNN7EXAMPLE"  # Don't do this!
)

# GOOD
import os
breadcrumb.init(
    db_path=os.getenv("BREADCRUMB_DB_PATH"),
)
```

---

## Threat Model

### In Scope

Breadcrumb protects against:

1. **Accidental secret logging**: Automatic redaction prevents secrets from being stored
2. **Unauthorized database access**: File permissions restrict access
3. **Data exposure via MCP**: Only SELECT queries allowed, no data modification
4. **Large data attacks**: Query timeouts and result size limits

### Out of Scope

Breadcrumb does NOT protect against:

1. **Malicious code execution**: Breadcrumb traces what your code does, but doesn't sandbox it
2. **Memory attacks**: In-memory data before redaction could be exposed by memory dumps
3. **Root/admin access**: Users with root access can read any file
4. **Supply chain attacks**: Compromised dependencies can access trace data
5. **Side-channel attacks**: Timing attacks, cache timing, etc.

### Assumptions

Security model assumes:

1. **Application code is trusted**: Breadcrumb traces what you tell it to
2. **Filesystem is secure**: Database file permissions are enforced
3. **Python runtime is secure**: No malicious Python packages
4. **User has appropriate access**: Database is only accessible to authorized users

---

## Responsible Disclosure

### Reporting Security Issues

If you discover a security vulnerability in Breadcrumb, please report it responsibly:

**Do NOT:**
- Create public GitHub issues for security vulnerabilities
- Disclose vulnerabilities on social media or forums
- Exploit vulnerabilities in production systems

**Please:**
1. Email security report to: [maintainer-email] (to be set)
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. Allow reasonable time for response (48-72 hours)
4. Do not disclose publicly until patch is released

### What to Report

Security issues include:

- **Secret redaction bypass**: Ways to bypass redaction and log secrets
- **SQL injection**: Ways to execute unsafe queries via MCP tools
- **Arbitrary file access**: Reading/writing files outside database
- **Privilege escalation**: Gaining unauthorized access to trace data
- **Denial of service**: Crashes, infinite loops, resource exhaustion
- **Code injection**: Executing arbitrary code via trace data

### What NOT to Report

Not considered security issues:

- **Feature requests**: Use GitHub issues for these
- **Configuration errors**: User misconfiguration
- **Intended behavior**: E.g., "database is not encrypted" (known limitation)
- **Denial of service via API misuse**: Rate limiting is user's responsibility

### Response Timeline

We aim for:

- **Initial response**: Within 72 hours
- **Severity assessment**: Within 1 week
- **Patch development**: 2-4 weeks depending on complexity
- **Public disclosure**: After patch release + 7 days

### Recognition

Security researchers who report valid vulnerabilities will be:

- Credited in CHANGELOG (if desired)
- Listed in security acknowledgments
- Offered early access to fixes for verification

---

## Security Roadmap

### Current Status (v0.1.0)

**Implemented:**
- ✅ Automatic secret redaction
- ✅ SQL injection prevention
- ✅ Query timeouts
- ✅ Read-only MCP tools
- ✅ Local-only storage

**Known Limitations:**
- ❌ No database encryption
- ❌ No audit logging
- ❌ No rate limiting
- ❌ No RBAC (Role-Based Access Control)

### Planned for v1.0

**Security enhancements:**
- [ ] Professional security audit
- [ ] Optional database encryption (via SQLCipher or similar)
- [ ] Audit logging (who queried what, when)
- [ ] Rate limiting for MCP tools
- [ ] Configurable redaction policies
- [ ] PII detection (beyond secrets)
- [ ] Data anonymization options

**Compliance:**
- [ ] GDPR compliance guide
- [ ] HIPAA considerations document
- [ ] SOC 2 readiness checklist

### Future Considerations

- [ ] End-to-end encryption for distributed tracing
- [ ] Zero-knowledge query protocols
- [ ] Differential privacy for aggregations
- [ ] Secure multi-party computation

---

## Best Practices Summary

### Development

✅ **DO:**
- Use default redaction patterns
- Add custom patterns for your app
- Test redaction with sample data
- Keep database in `.gitignore`
- Use sampling for performance tests

❌ **DON'T:**
- Commit database to version control
- Disable redaction without good reason
- Trace third-party library internals
- Log unredacted data manually

### Production

✅ **DO:**
- Use selective instrumentation
- Implement data retention policies
- Restrict database file permissions
- Monitor database size
- Consider disabling in production

❌ **DON'T:**
- Trace 100% of production traffic
- Store database in world-readable location
- Keep traces indefinitely
- Expose MCP server to network (use stdio)

### Security

✅ **DO:**
- Review redaction patterns regularly
- Audit database contents periodically
- Update Breadcrumb to latest version
- Report security issues responsibly
- Document your security configuration

❌ **DON'T:**
- Store unencrypted PII
- Share database files
- Run as root/admin user
- Expose database to public network
- Trust user input in queries

---

## Questions?

For security questions or concerns:

1. **Security vulnerabilities**: Report via responsible disclosure (above)
2. **Security configuration**: See [QUICKSTART.md](QUICKSTART.md)
3. **Best practices**: See this document
4. **General questions**: GitHub Issues (for non-security topics)

**Stay secure!**
