# Identity and scope

## Resolution order

`region`: explicit tool argument → `HUAWEI_REGION` → ask the user.

`project_id`: explicit tool argument → `HUAWEI_PROJECT_ID` → ask the user.

The MCP deliberately does not depend on IAM and does not guess project IDs. A
project ID is regional and must match the selected region. Keep resolved values
in the current conversation; never write them into this Skill or repository.

## Configuration errors

- Missing AK/SK: update the selected client's `huawei-lts` MCP `env` or
  `environment` section and restart it.
- Empty results: confirm the region/project pair before concluding there are no resources.
- Permission failures: verify the credential has the required LTS read or write policy.
