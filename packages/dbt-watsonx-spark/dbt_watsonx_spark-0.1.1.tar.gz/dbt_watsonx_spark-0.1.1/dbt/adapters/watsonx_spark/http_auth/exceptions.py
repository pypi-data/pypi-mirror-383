from dbt_common.exceptions import DbtConfigError, DbtRuntimeError, DbtDatabaseError


class BaseDbtError(DbtRuntimeError):
    pass


class TokenRetrievalError(BaseDbtError):
    """Error raised when token retrieval fails."""
    def __init__(self, status_code=None, message=None):
        self.status_code = status_code
        msg = "Failed to retrieve authentication token"
        if status_code:
            msg += f". Status code: {status_code}"
        if message:
            msg += f". Details: {message}"
        super().__init__(msg)


class InvalidCredentialsError(BaseDbtError):
    """Error raised when credentials are invalid."""
    def __init__(self, message=None, env_type=None):
        self.env_type = env_type
        msg = "Authentication failed: Invalid credentials provided"
        
        # Add environment-specific documentation links
        if env_type == "SAAS":
            msg += (". Please check your credentials and refer to the SaaS setup documentation: "
                   "https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-dbt_watsonx_spark_conf")
        elif env_type == "CPD":
            msg += (". Please check your credentials and refer to the CPD setup documentation: "
                   "https://www.ibm.com/docs/en/watsonxdata/standard/2.1.x?topic=spark-configuration-setting-up-your-profile")
        else:
            msg += ". Please check your credentials and refer to the setup documentation."
            
        if message:
            msg += f" Additional details: {message}"
            
        super().__init__(msg)


class CatalogDetailsError(BaseDbtError):
    """Error raised when catalog details retrieval fails."""
    def __init__(self, catalog_name=None, status_code=None, message=None):
        self.status_code = status_code
        msg = "Failed to retrieve catalog details"
        if catalog_name:
            msg += f" for catalog '{catalog_name}'"
        if status_code:
            msg += f". Status code: {status_code}"
        if message:
            msg += f". Details: {message}"
        super().__init__(msg)


class ConnectionError(DbtRuntimeError):
    """Error raised when connection to query server fails."""
    def __init__(self, message=None, host=None):
        msg = "Failed to connect to query server"
        if host:
            msg += f" at {host}"
        if message:
            msg += f". Details: {message}"
        super().__init__(msg)


class AuthenticationError(DbtRuntimeError):
    """Error raised when authentication fails."""
    def __init__(self, message=None):
        msg = "Authentication failed"
        if message:
            msg += f". Details: {message}"
        super().__init__(msg)

