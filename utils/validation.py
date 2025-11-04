from datetime import datetime
import re


class ValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def require_json(payload):
    if payload is None:
        raise ValidationError("Request body must be JSON", 400)
    if not isinstance(payload, dict):
        raise ValidationError("JSON body must be an object", 400)
    return payload


def validate_fields(data: dict, schema: dict):
    for field_name, rules in schema.items():
        is_required = rules.get('required', False)
        expected_type = rules.get('type')
        value = data.get(field_name)

        if is_required and (value is None or (isinstance(value, str) and value.strip() == '')):
            raise ValidationError(f"{field_name} is required", 400)

        if value is None:
            continue

        # Type checks
        if expected_type == 'string' and not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", 400)
        if expected_type == 'number' and not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name} must be a number", 400)
        if expected_type == 'integer' and not isinstance(value, int):
            raise ValidationError(f"{field_name} must be an integer", 400)

        # String constraints
        if isinstance(value, str):
            min_len = rules.get('min_length')
            max_len = rules.get('max_length')
            if min_len is not None and len(value) < min_len:
                raise ValidationError(f"{field_name} must be at least {min_len} characters", 400)
            if max_len is not None and len(value) > max_len:
                raise ValidationError(f"{field_name} must be at most {max_len} characters", 400)

        # Numeric constraints
        if isinstance(value, (int, float)):
            min_val = rules.get('min')
            max_val = rules.get('max')
            if min_val is not None and value < min_val:
                raise ValidationError(f"{field_name} must be >= {min_val}", 400)
            if max_val is not None and value > max_val:
                raise ValidationError(f"{field_name} must be <= {max_val}", 400)

        # Enum
        if 'allowed' in rules and value not in rules['allowed']:
            allowed_list = ', '.join(map(str, rules['allowed']))
            raise ValidationError(f"{field_name} must be one of: {allowed_list}", 400)

        # Email
        if rules.get('format') == 'email':
            if not isinstance(value, str) or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
                raise ValidationError("Invalid email format", 400)


def parse_date(value: str, field_name: str, fmt: str = '%Y-%m-%d'):
    try:
        return datetime.strptime(value, fmt)
    except Exception:
        raise ValidationError(f"{field_name} must match format {fmt}", 400)


