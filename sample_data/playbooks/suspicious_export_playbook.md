# Suspicious Warehouse Export Playbook

## Purpose

This playbook helps investigate suspicious warehouse export activity involving large downloads, external destinations, or unusual users.

## Common Symptoms

- Large export to external_sftp
- Bulk table export from customer_profiles or payments_curated
- Export performed by external_vendor
- Export happens after high-risk login
- Export happens after permission_added or iam_policy_updated event
- Export is blocked or fails due to token or access issue

## Investigation Steps

1. Identify export events with high or critical risk_level.
2. Check rows_exported and file_size_mb.
3. Review destination for external_sftp, email_attachment, or api_client.
4. Check security_logs for high-risk login_failure, mfa_failure, or unusual role_assumed events near the export time.
5. Check admin_events for permission_added, iam_policy_updated, or s3_bucket_policy_updated before the export.
6. Check api_token_events for token_used or token_failed_auth by the same service or user.
7. Confirm whether the export was approved and expected.
8. Escalate to security if the export is unauthorized.

## Severity Guidance

Critical severity if:
- Sensitive dataset was exported externally
- Export follows suspicious login or permission change
- External vendor account is involved
- Export volume is unusually large

Medium severity if:
- Export is large but expected
- Export destination is internal
- No suspicious security or admin activity is found

## Recommended Remediation

- Disable affected token or user session
- Review access permissions
- Block external export destination if unauthorized
- Preserve logs for investigation
- Notify security and data governance teams