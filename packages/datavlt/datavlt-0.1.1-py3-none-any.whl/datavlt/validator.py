def validate_record(record: dict) -> bool:
    if not isinstance(record, dict):
        return False

    for key, expected_type in required_fields.items():
        if key not in record:
            return False
        if not isinstance(record[key], expected_type):
            return False

    return True
