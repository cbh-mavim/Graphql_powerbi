from typing import Any, Dict, Optional
from gql.types import CombinedDatabasesType
from gql.utils.datetime import parse_mavim_date
from auth import User 

def transform_to_combined_databases(row: Dict[str, Any], user: Optional[User] = None) -> CombinedDatabasesType:
    
    is_admin = user and "Reader" in user.roles

    connection_string_value = row['connection_string'] if is_admin else None
    database_name_value = row["database_name"] if is_admin else None

    return CombinedDatabasesType(
        database_id=row['database_id'],
        connection_string=connection_string_value,
        database_name=database_name_value,
        company_guid=row['company_guid'],
        created_date=parse_mavim_date(row['created_date']),
        modified_date=parse_mavim_date(row['modified_date']),
        primary_region=row['primary_region'],
        company_id=row['company_id'],
        company_name=row['company_name'],
        reference_db=row['reference_db'],
        allowed_db_size_mb=row['allowed_db_size_mb'],
        db_size_mb=row['db_size_mb'],
        customer_name_and_id=row['customer_name_and_id']
    )
