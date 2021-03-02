# personium-migration-tools

Personium migration tools needed for modifying incompability between updating versions.

## Requirements

These tools support python 3.6 or lator.

## Tools

### Owner Update

To solve the owner information in cell documents in DB, this tool update the schema format from old-style to extended localunit scheme (since v1.7.18).

#### Usage

```bash
cd /path/to/personium-migration-tools/downloaded/
python3 bin/owner_update_1_7_18.py <es_host>
```

Write your elasticsearch host in place of `<es_host>`.

#### Option

- `--port` : You can specify the port which is used to connect elastic search
