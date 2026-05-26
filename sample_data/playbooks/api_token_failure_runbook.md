# API Token Failure Runbook

## Purpose

This runbook helps investigate data pipeline failures caused by expired, revoked, rotated, or invalid API tokens.

## Common Symptoms

- Pipeline fails with api_token_expired
- Pipeline fails with token_failed_auth
- Pipeline fails shortly after secret_rotated or token_rotated event
- Service account authentication failures increase
- Downstream API calls return unauthorized or forbidden errors

## Investigation Steps

1. Identify the failed pipeline run from pipeline_logs.
2. Check whether the error message contains api_token_expired or authentication failure.
3. Search api_token_events for token_expired, token_revoked, token_rotated, or token_failed_auth events within 30 minutes before the failed run.
4. Search admin_events for secret_rotated, permission_added, permission_removed, or iam_policy_updated events near the failure time.
5. Search security_logs for high-risk login_failure, mfa_failure, or role_assumed events involving admin or service accounts.
6. Confirm whether the affected service_name matches the failed pipeline_name.
7. Verify whether the token belongs to the correct service account.
8. Refresh or rotate the token if needed.
9. Re-run the failed pipeline after validating credentials.

## Severity Guidance

Critical severity if:
- Token failure affects production pipeline
- Token was revoked unexpectedly
- High-risk admin login happened before the token event
- Multiple services fail using the same token

Medium severity if:
- Token expired normally
- Failure is limited to one non-critical job
- No suspicious security activity is found

## Recommended Remediation

- Rotate affected credentials
- Update pipeline secret references
- Validate IAM/service account permissions
- Re-run the failed job
- Add alerting for token expiration before scheduled jobs