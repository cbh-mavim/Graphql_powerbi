import strawberry
from typing import Optional
from gql.utils.datetime import DateTimeISO
    
@strawberry.type
class CompanyType:
    customer_id: int
    customer_name: Optional[str]
    created_date: Optional[DateTimeISO]
    modified_date: Optional[DateTimeISO]
    termination_date: Optional[DateTimeISO]
    terminated_date: Optional[DateTimeISO]
    crm_id: Optional[str]
    number_of_databases: Optional[int]
    number_of_portal_users: Optional[int]
    external_customer_id: Optional[str]
    is_partner: Optional[bool]
    partner_customer_id: Optional[int]
    is_onboarded_to_improve: Optional[bool]
    onboarded_to_improve_date: Optional[DateTimeISO]
    exact_id: Optional[float]
    version_number: Optional[str]
    company_guid: Optional[str]
    domain_name: Optional[str]
    app_id: Optional[str]
    customer_name_and_id: Optional[str]
    crm_url:Optional[str]
    

    