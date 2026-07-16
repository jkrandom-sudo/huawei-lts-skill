# Prompt examples

```text
Use huawei-lts to list log groups in {region}, project_id={project_id}, and summarize stream counts.
```

```text
Search {log_group_id}/{log_stream_id} for {keyword} during {start_time}–{end_time}.
Return a concise conclusion and redacted examples, not the full JSON response.
region={region}, project_id={project_id}.
```

```text
Inspect keyword and SQL alarm rules in {region}. Do not change anything.
project_id={project_id}.
```

```text
Prepare to update {resource_id}. First show current state and impact, then wait
for my explicit confirmation before calling an Update or Delete tool.
```
