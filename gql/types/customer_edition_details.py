import strawberry
from typing import Optional
from gql.utils.datetime import DateTimeISO
      
@strawberry.type
class CustomerEditionDetailsType:
    customer_id: int
    customer_edition_id: int
    edition_id: int
    edition_name: Optional[str]
    edition_description: Optional[str]
    edition_is_active: Optional[bool]
    edition_quantity: Optional[int]
    edition_created_date: Optional[DateTimeISO]
    edition_modified_date: Optional[DateTimeISO]
    edition_deleted_date: Optional[DateTimeISO]
    