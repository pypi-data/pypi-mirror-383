from sqlalchemy import create_engine, MetaData, text
from retrying import retry
import mysql.connector
from typing import Dict, Any
import os



class AccessRightHelper:
    """Access rights helper with configurable database connection."""
    
    def __init__(self) -> None:
        MYSQL_HOSTNAME_INTERNAL=os.environ["MYSQL_HOSTNAME_INTERNAL"]
        MYSQL_PORT_INTERNAL=os.environ["MYSQL_PORT_INTERNAL"]
        MYSQL_DATABASE_NAME=os.environ["MYSQL_DATABASE_NAME"]
        MYSQL_USER_NAME=os.environ["MYSQL_USER_NAME"]
        MYSQL_USER_PASSWORD=os.environ["MYSQL_USER_PASSWORD"]
        
        self.hostname = MYSQL_HOSTNAME_INTERNAL
        self.port = MYSQL_PORT_INTERNAL
        self.database = MYSQL_DATABASE_NAME
        self.username = MYSQL_USER_NAME
        self.password = MYSQL_USER_PASSWORD
        
        # Define the database connection
        self.database_url = f"mysql+mysqlconnector://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"
        
        # Create the SQLAlchemy engine
        self.engine = create_engine(self.database_url, echo=False)
        
        # Reflect the database schema (load metadata)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def get_app_access_rights(self, app_name: str, email_address: str) -> Dict[str, Any]:
        """Get application access rights for a user."""
        query = text("""
            SELECT EmailAddress, IsLoginEnabled, IsFeature1Enabled, IsFeature2Enabled, IsFeature3Enabled
            FROM AppAccessRights
            WHERE AppName = :app_name 
            AND lower(EmailAddress) = lower(:email_address)
            UNION
            SELECT EmailAddress, IsLoginEnabled, IsFeature1Enabled, IsFeature2Enabled, IsFeature3Enabled
            FROM AppAccessRights
            WHERE AppName = :app_name 
            AND lower(EmailAddress) = 'everyone' 
            AND NOT EXISTS (
                SELECT 1
                FROM AppAccessRights
                WHERE AppName = :app_name 
                AND lower(EmailAddress) = lower(:email_address)
            )
        """)

        with self.engine.connect() as connection:
            result = connection.execute(query, {'app_name': app_name, 'email_address': email_address})
            app_access_rights_dict = {}
            for row in result.mappings():
                user_properties = {
                    'IsLoginEnabled': row['IsLoginEnabled']==1,
                    'IsFeature1Enabled': row['IsFeature1Enabled']==1,
                    'IsFeature2Enabled': row['IsFeature2Enabled']==1,
                    'IsFeature3Enabled': row['IsFeature3Enabled']==1
                }
                app_access_rights_dict[row['EmailAddress']] = user_properties

        return app_access_rights_dict


# Legacy function for backward compatibility
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def get_app_access_rights(app_name: str, email_address: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    helper = AccessRightHelper()
    return helper.get_app_access_rights(app_name, email_address) 