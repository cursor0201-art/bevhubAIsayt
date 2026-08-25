# SYSTEM_PROMPT_PART_09.md
# SECURITY BIBLE

==================================================
MISSION
==================================================

Security is not a feature.

Security is a core architecture principle.

Every component must be designed assuming attackers exist.

Trust nothing.

Verify everything.

==================================================
ZERO TRUST
==================================================

Never trust:

Users

Browsers

Requests

Headers

Files

IP Addresses

Third-party services

Everything must be verified.

==================================================
AUTHENTICATION
==================================================

Support

Email + Password

Google OAuth

GitHub OAuth

Microsoft OAuth

Apple Sign In

Passkeys Ready

Magic Links (Future)

==================================================
PASSWORDS
==================================================

Never store passwords.

Store only strong password hashes.

Enforce:

Minimum Length

Uppercase

Lowercase

Numbers

Special Characters

Password History

Password Expiration (Enterprise)

==================================================
SESSIONS
==================================================

Every session stores

Device

Browser

IP

Country

Login Time

Last Activity

Refresh Token

Session Status

Users can revoke any session.

==================================================
JWT
==================================================

Short-lived Access Token

Long-lived Refresh Token

Automatic Rotation

Revocation Support

Device Binding Ready

==================================================
MULTI FACTOR AUTH
==================================================

Support

Authenticator Apps

Email OTP

Recovery Codes

Enterprise MFA Policies

==================================================
PERMISSIONS
==================================================

RBAC

Role Based Access Control

Permissions never hardcoded.

Everything configurable.

==================================================
API SECURITY
==================================================

Rate Limiting

Request Validation

Input Sanitization

Output Sanitization

Strict Content Types

Versioning

Idempotency

Request Size Limits

==================================================
DATABASE SECURITY
==================================================

Parameterized Queries

Transactions

Least Privilege

Encrypted Backups

Encrypted Connections

Audit Logs

==================================================
FILE SECURITY
==================================================

Validate MIME Type

Validate Size

Virus Scan Ready

Random File Names

Private Storage

Signed URLs

Image Processing Isolation

==================================================
PROMPT SECURITY
==================================================

Protect against

Prompt Injection

System Prompt Leakage

Jailbreak Attempts

Data Extraction

Model Abuse

Context Poisoning

Sensitive Prompt Exposure

==================================================
SECRETS
==================================================

Never hardcode

API Keys

Passwords

Secrets

Tokens

Store in environment variables or a secure secrets manager.

==================================================
ENCRYPTION
==================================================

TLS Everywhere

Encrypted Storage

Encrypted Tokens

Encrypted Sensitive Data

==================================================
MONITORING
==================================================

Detect

Brute Force

Credential Stuffing

Spam

Bot Activity

API Abuse

Payment Fraud

Account Takeover

==================================================
DISASTER RECOVERY
==================================================

Automatic Backups

Database Recovery

Rollback Strategy

Multi-region Ready

Recovery Testing

==================================================
AUDIT
==================================================

Log every critical action.

Immutable logs preferred.

Never silently ignore security events.

==================================================
SECURITY PRINCIPLE
==================================================

Security must never significantly reduce usability.

Protect users without making the product frustrating.

==================================================
END OF PART 09
