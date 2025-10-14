SELECT '{PROJECT_CODE}'            as project_code,
       CURRENT_TIMESTAMP           as refresh_timestamp,
       c.table_schema,
       c.table_name,
       c.column_name,
       CASE
           WHEN c.data_type = 'datetime' THEN 'datetime'
           WHEN c.data_type = 'datetime2' THEN 'datetime'
           WHEN c.data_type = 'varchar'
               THEN 'varchar(' + CAST(c.character_maximum_length AS VARCHAR) + ')'
           WHEN c.data_type = 'char' THEN 'char(' + CAST(c.character_maximum_length AS VARCHAR) + ')'
           WHEN c.data_type = 'numeric' THEN 'numeric(' + CAST(c.numeric_precision AS VARCHAR) + ',' +
                                             CAST(c.numeric_scale AS VARCHAR) + ')'
           ELSE c.data_type END AS column_type,
       CASE
           WHEN c.data_type LIKE '%char' OR c.data_type LIKE '%binary'
               THEN c.data_type + '(' + CAST(c.character_maximum_length AS VARCHAR) + ')'
           WHEN c.data_type IN ('datetime2', 'datetimeoffset', 'time')
               THEN c.data_type + '(' + CAST(c.datetime_precision AS VARCHAR) + ')'
           WHEN c.data_type IN ('numeric', 'decimal')
               THEN c.data_type + '(' + CAST(c.numeric_precision AS VARCHAR) + ','
                   + CAST(c.numeric_scale AS VARCHAR) + ')'
       ELSE c.data_type END AS db_data_type,
       c.character_maximum_length,
       c.ordinal_position,
       CASE
           WHEN LOWER(c.data_type) LIKE '%char%'
               THEN 'A'
           WHEN c.data_type = 'bit'
               THEN 'B'
           WHEN c.data_type = 'date'
               OR c.data_type LIKE '%datetime%'
               THEN 'D'
           WHEN c.data_type = 'time'
               THEN 'T'
           WHEN c.data_type IN ('real', 'float', 'decimal', 'numeric')
               OR c.data_type LIKE '%int'
               OR c.data_type LIKE '%money'
               THEN 'N'
           ELSE
               'X'
       END AS general_type,
       CASE WHEN c.numeric_scale > 0 THEN 1 ELSE 0 END AS is_decimal
FROM information_schema.columns c
WHERE c.table_schema = '{DATA_SCHEMA}' {TABLE_CRITERIA}
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
