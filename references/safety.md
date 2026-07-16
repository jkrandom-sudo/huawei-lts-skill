# Safety rules

## Confirmation required

Require explicit confirmation before Delete, Update, enable/disable, checkpoint
changes, and batch Create operations. Include resource ID/name, region,
project_id, and irreversible or availability impact in the confirmation prompt.

## Credential and data handling

- Never display `HUAWEI_ACCESS_KEY` or `HUAWEI_SECRET_KEY`.
- Never commit credentials, real tenant IDs, or business resource names.
- Redact passwords, tokens, cookies, authorization headers, and personal data
  from representative log records.
- Prefer summaries over complete raw log payloads.

## Failure behavior

Do not retry invalid parameters or permission failures blindly. Retry rate limits,
timeouts, and transient 5xx responses only when safe, with a bounded attempt count.
When MCP is unavailable, explain configuration checks instead of inventing output.
