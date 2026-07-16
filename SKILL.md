---
name: huawei-lts
description: >-
  Operate Huawei Cloud Log Tank Service (LTS) through the huawei-lts MCP server.
  Use whenever the user mentions LTS, 云日志, 日志组, 日志流, ListLogs,
  关键词告警, SQL 告警, 日志转储, 日志接入, host groups, or Huawei Cloud
  log troubleshooting. Discover actual MCP tool names in the current session,
  default to read-only inspection, and never invent cloud results.
---

# Huawei Cloud LTS

Use the configured `huawei-lts` MCP server for all cloud operations. Do not call
unrelated CLIs or fabricate results when MCP is unavailable.

## Before calling a tool

1. Resolve `region`: explicit user value, then `HUAWEI_REGION`, otherwise ask.
2. Resolve `project_id`: explicit user value, then `HUAWEI_PROJECT_ID`, otherwise ask.
3. Discover the actual MCP tool names exposed in this session. Client prefixes vary.
4. Choose the narrowest read operation that can answer the request.

Read [references/identity.md](references/identity.md) when scope is missing or
ambiguous. Read [references/tools.md](references/tools.md) only when selecting
an unfamiliar operation.

## Common routing

| Intent | Tool sequence |
|---|---|
| Discover logs | `ListLogGroups` → `ListLogStream` or `ListLogStreams` |
| Search/troubleshoot | optional `ListLogHistogram` → `ListLogs` → optional `ListLogContext` |
| Structured query | `ListQueryStructuredLogs` or `ListStructuredLogsWithTimeRange` |
| Inspect alarms | `ListKeywordsAlarmRules`, `ListSqlAlarmRules`, `ListActiveOrHistoryAlarms` |
| Inspect transfers | `ListTransfers` |
| Inspect collection | `ListAccessConfig` → `ListHostGroup` → `ListHost` |

For detailed sequences, pagination, and output guidance, read
[references/workflows.md](references/workflows.md).

## Safety boundary

- Default to `List*` and `Show*`.
- Before Update, Delete, enable/disable, or batch Create: show the target resource,
  region/project_id, intended change, and impact; wait for explicit confirmation.
- After a write, use a read operation to verify the resulting state.
- Never echo AK/SK or place credentials in files other than the user's MCP config.
- Summarize logs and redact obvious secrets; do not dump large raw responses by default.

Read [references/safety.md](references/safety.md) before any write operation.

## Response format

Lead with the conclusion and queried time range. Then give resource identifiers,
match counts, representative redacted evidence, and the next recommended action.
State missing configuration or MCP errors plainly.
