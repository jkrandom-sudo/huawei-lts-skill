# LTS workflows

## Log discovery and search

1. List groups, select the target by name, and retain its ID.
2. List streams for that group and retain the target stream ID.
3. Search the smallest useful UTC millisecond time range.
4. Use histogram first when the range is large or event timing is unknown.
5. Follow returned pagination fields; do not restart from the first page.
6. Fetch context only around representative lines.

Report the group/stream, time range, count, representative redacted records, and
whether a wider range or different stream is warranted.

## Alarm inspection

List keyword and SQL rules before active/history alarms. Correlate rule status,
severity, query, stream, and notification destination. Never update a rule until
the current representation and exact proposed difference are shown.

## Transfers and collection

For transfers, list first and group by source group/stream and destination type.
For collection, inspect access configs, then host groups and hosts. Treat path,
blacklist, whitelist, TTL, and destination changes as impactful writes.

## Write verification

Read current state → describe exact change and impact → obtain explicit approval
→ execute one bounded write → read the same resource again → report the observed state.
