# Complete LTS tool index

Tool names below are logical names. Use the actual names exposed by the current
MCP session; clients may add a server prefix.

## Log groups, streams, and search

- `ListLogGroups`, `CreateLogGroup`, `UpdateLogGroup`, `DeleteLogGroup`
- `ListLogStream`, `ListLogStreams`, `CreateLogStream`, `UpdateLogStream`, `DeleteLogStream`
- `CreateLogStreamIndex`
- `ListLogs`, `ListLogHistogram`, `ListLogContext`
- `ListQueryStructuredLogs`, `ListStructuredLogsWithTimeRange`, `ListHistorySql`

## Alarms and notifications

- `ListKeywordsAlarmRules`, `CreateKeywordsAlarmRule`, `UpdateKeywordsAlarmRule`, `DeleteKeywordsAlarmRule`
- `ListSqlAlarmRules`, `CreateSqlAlarmRule`, `UpdateSqlAlarmRule`, `DeleteSqlAlarmRule`
- `UpdateAlarmRuleStatus`, `ListActiveOrHistoryAlarms`, `DeleteActiveAlarms`
- `ListNotificationTopics`, `ListNotificationTemplate`, `ListNotificationTemplates`
- `ShowNotificationTemplate`, `CreateNotificationTemplate`, `UpdateNotificationTemplate`, `DeleteNotificationTemplate`

## Transfers and collection

- `ListTransfers`, `CreateTransfer`, `UpdateTransfer`, `DeleteTransfer`
- `CreateLogDumpObs`, `RegisterDmsKafkaInstance`
- `ListAccessConfig`, `CreateAccessConfig`, `UpdateAccessConfig`, `DeleteAccessConfig`
- `ListHostGroup`, `CreateHostGroup`, `UpdateHostGroup`, `DeleteHostGroup`, `ListHost`
- `EnableLogCollection`, `DisableLogCollection`

## Structured templates and saved searches

- `ShowStructTemplate`, `ListStructTemplate`, `ListBreifStructTemplate`
- `CreateStructTemplate`, `UpdateStructTemplate`, `DeleteStructTemplate`
- `CreateStructConfig`, `UpdateStructConfig`
- `CreateSearchCriterias`, `ListCriterias`, `ListQueryAllSearchCriterias`, `DeleteSearchCriterias`
- `Createfavorite`, `Deletefavorite`, `CreateTags`

## Dashboards, mappings, and administration

- `CreateDashBoard`, `CreateDashboardGroup`, `DeleteDashboard`, `ListCharts`
- `CreateAomMappingRules`, `ShowAomMappingRule`, `ShowAomMappingRules`
- `UpdateAomMappingRules`, `DeleteAomMappingRules`
- `CreateAgencyAccess`, `ShowAdminConfig`
- `ShowLogConvergeConfig`, `UpdateLogConvergeConfig`, `ShowMemberGroupAndStream`
- `ListTimeLineTrafficStatistics`, `ListTopnTrafficStatistics`, `UpdateSwitch`

## Consumer groups and cursors

- `CreateConsumerGroup`, `ListConsumerGroup`, `ListDetailsConsumerGroup`, `DeleteConsumerGroup`
- `ConsumerGroupHeartBeat`, `ShowCursorByTime`, `ShowCursorTime`
- `ShowLogStreamShards`, `UpdateCheckPoint`
