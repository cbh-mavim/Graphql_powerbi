import strawberry
from strawberry.types import Info 
from typing import List
from gql.services.data_service import DataService
from gql.types import CombinedDatabasesType
from gql.config import combined_databases as PATH
from gql.resolvers.transformers import transform_to_combined_databases
from auth import User 
 

company_service = DataService(path=PATH,
                              entity_type=CombinedDatabasesType,
                              transform_func=transform_to_combined_databases)
 
@strawberry.type
class Query: 
    @strawberry.field
    def get_combined_databases(self, info: Info) -> List[CombinedDatabasesType]:
    
        return company_service.get_data(info=info)
