# Security Design Notes (Not a Compliance Attestation)

This legacy filename is retained so existing links do not break. CareRoute is a hackathon prototype and has not been independently audited, certified, or deployed under an organizational HIPAA compliance program. The presence of encryption and audit-related code does not make the system HIPAA compliant.

Do not use real patient or protected health information with this repository as-is.

## Implemented security-related code

- `backend/database/encryption.py` derives a Fernet key from `HIPAA_ENCRYPTION_PASSWORD` and an optional `HIPAA_ENCRYPTION_SALT`, then encrypts selected patient fields.
- `backend/database/audit.py` defines audit-event helpers.
- `backend/database/models.py` defines patient, booking, orchestration, and audit-log models.
- `backend/database/connection.py` requires `DATABASE_URL` and configures a SQLAlchemy connection pool.
- `backend/knowledge_base.py` encrypts values held by the prototype knowledge base. It derives a stable key from environment configuration when available and otherwise uses a warned, ephemeral process-local key.
- Secrets and external service URLs are read from environment variables in the current deployment configuration.

These are implementation facts, not evidence that every request path uses the controls correctly.

## Known gaps

- The FastAPI surface does not implement a complete authentication and authorization model.
- CORS is broadly configured in `backend/main_backend.py`.
- The database connection currently disables PostgreSQL SSL for local development.
- External-agent transport security depends on deployment-specific endpoint configuration.
- Some code paths fall back to local JSON or in-memory state.
- Logging, data minimization, retention, deletion, backup, key rotation, incident response, and access review have not been validated end to end.
- No threat model, penetration test, independent security review, business associate agreements, workforce procedures, or compliance assessment is included.

## Configuration

The database layer requires `DATABASE_URL`. Stable encryption requires `HIPAA_ENCRYPTION_PASSWORD`; use a deployment-specific `HIPAA_ENCRYPTION_SALT` when keys must remain stable across processes. Store these values in an external secret manager or local untracked environment configuration—never in the repository.

The tracked `backend/hipaa_encryption.key` file was removed from the current tree. That removal does not erase it from Git history and does not substitute for rotating any value that may have been exposed.

## Before handling sensitive data

At minimum, a real deployment would need:

1. A documented data-flow and threat model covering every service and external agent.
2. Strong identity, authorization, tenant isolation, and least-privilege controls.
3. TLS for all network and database connections, with verified certificates.
4. Managed secret storage, rotation, revocation, and separation by environment.
5. Verified audit coverage that avoids placing sensitive payloads in logs.
6. Defined retention, deletion, backup, recovery, and breach-response procedures.
7. Dependency, container, infrastructure, and application security testing.
8. Review by the organization's security, privacy, and legal/compliance owners.

For regulatory requirements, use current official guidance from the [U.S. Department of Health and Human Services](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html). This document is an engineering inventory, not legal advice.
