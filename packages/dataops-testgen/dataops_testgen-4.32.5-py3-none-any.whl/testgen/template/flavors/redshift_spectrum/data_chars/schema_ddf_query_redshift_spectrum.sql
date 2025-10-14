SELECT '{PROJECT_CODE}' AS project_code,
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' AS refresh_timestamp,
    c.schemaname AS table_schema,
    c.tablename AS table_name,
    c.columnname AS column_name,
    c.external_type AS column_type,
    c.external_type AS db_data_type,
    NULLIF(
        REGEXP_SUBSTR(c.external_type, 'char\\(([0-9]+)\\)', 1, 1, 'e'),
        ''
    ) AS character_maximum_length,
    c.columnnum AS ordinal_position,
    CASE
        WHEN c.external_type = 'string'
            OR c.external_type ILIKE 'varchar%'
            OR c.external_type ILIKE 'char%'
            THEN 'A'
        WHEN c.external_type = 'boolean'
            THEN 'B'
        WHEN c.external_type IN ('date', 'timestamp')
            THEN 'D'
        WHEN c.external_type IN ('long', 'double', 'float')
            OR c.external_type ILIKE '%int%'
            OR c.external_type ILIKE 'decimal%'
            THEN 'N'
        ELSE 'X'
    END AS general_type,
    CASE
        WHEN REGEXP_SUBSTR(c.external_type, 'decimal\\([0-9]+,([0-9]+)\\)', 1, 1, 'e') > 0
            THEN 1
        ELSE 0
    END AS is_decimal
FROM svv_external_columns c
WHERE c.schemaname = '{DATA_SCHEMA}'
    {TABLE_CRITERIA}
ORDER BY c.schemaname,
    c.tablename,
    c.columnnum