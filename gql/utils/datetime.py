from datetime import datetime
import pytz
import strawberry
from dateutil import parser
# Custom scalar for datetimeoffset
@strawberry.scalar
class DateTimeISO:

    @staticmethod
    def serialize(value) -> str:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)  # Convert string to datetime
        return value.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD


def parse_mavim_date(date_str: str) -> str | None:
    """
    Parse a date string and convert it to Europe/Amsterdam timezone.
    Returns None if the input is None or empty string.
    
    Args:
        date_str: The date string to parse
        
    Returns:
        Timezone-aware datetime object or None if input is invalid
    """
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        return parser.parse(date_str).astimezone(pytz.timezone("Europe/Amsterdam"))
    except (ValueError, TypeError):
        return None 