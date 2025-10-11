"""A module containing the Service Principal credential class"""
from azol.credentials.entraid_credential import EntraIdCredential
from azol.constants import OAUTHFLOWS
from cryptography.hazmat.primitives.serialization import pkcs12
import base64
import os
import logging
import requests

class ADOWorkloadFederationCredential( EntraIdCredential ):
    """
        A credential to log in as a service principal

        IMPORTANT: two dependencies must be met in order to use this credential in a devops pipeline.

                1)
                    This access token must be in the local environment variables in the azure devops
                    pipeline execution environment. to ensure that this is the case, request the
                    system access token in the environment variables of the azure devops job. for example,
                    in the yaml pipeline file, use the following script task to set the system access token
                    to the variable "SYSTEM_ACCESSTOKEN":

                        - script |
                            env
                          env:
                            SYSTEM_ACCESSTOKEN: $(System.AccessToken)

                2) 
                    The system access token will not be able to get an oidc token for a service
                    endpoint unless that service endpoint is used in another task within the same
                    job. The easiest way to make this work is to use the Azure CLI task, and run
                    azol within that task. For example:


                        - task: AzureCLI@2
                            inputs:
                                azureSubscription: 'your-service-connection-name'
                                scriptType: 'bash'
                                scriptLocation: 'InlineScript'
                                inlineScript: |
                                  pip install azol
                                  python -c "
                                  from azol import *;
                                  cred=ADOWorkloadFederationCredential(
                                    client_id='your-client-id', 
                                    service_endpoint_id='your-service-endpoint-id' );
                                  client=ArmClient(cred=cred, tenant='yourtenant.com');
                                  client.fetch_token();
                                  token=client.get_current_token()"
                          env:
                            SYSTEM_ACCESSTOKEN: $(System.AccessToken)
    """

    supportedOAuthFlows = [ OAUTHFLOWS.CLIENT_CREDENTIALS ]
    credentialType="app"
    default_oauth_flow=OAUTHFLOWS.CLIENT_CREDENTIALS
    def __init__( self, client_id, service_endpoint_id, *args, **kwargs ):
        super().__init__( *args, **kwargs)
        self._client_id=client_id
        self._credential_type="ado_oidc"
        self._service_endpoint_id = service_endpoint_id

    def get_credential_type( self ):
        """
            Returns: string - secret or x509, depending on what type of secret was defined for
                     the service principal
        """
        return self._credential_type

    def get_service_endpoint( self ):
        """
            Get the service endpoint id used for this cert

            Returns: azure devops service endpoint id
        """
        return self._service_endpoint_id

    def get_system_access_token( self, var_name="SYSTEM_ACCESSTOKEN" ):
        """
            Get the system access token for the workload federation credential. 

            IMPORTANT: A dependency must be met in order to use this credential in a devops pipeline.

                    This access token must be in the local environment variables in the azure devops
                    pipeline execution environment. to ensure that this is the case, request the
                    system access token in the environment variables of the azure devops job. for example,
                    in the yaml pipeline file, use the following script task to set the system access token
                    to the variable "SYSTEM_ACCESSTOKEN":

                        - script |
                            env
                          env:
                            SYSTEM_ACCESSTOKEN: $(System.AccessToken)

            Args:
                - var_name: The environment variable name that contains the system access token.
                            Must match the variable set in the yaml pipeline

            Returns: The system access token for the Azure DevOps job
        """
        try:
            system_access_token=os.environ.get(var_name)
        except Exception as msg:
            logging.error("could not get system access token")

        return system_access_token

    def get_oidc_url( self ):
        """
            Gets the OIDC url from the azure devops execution environment. This
            is saved in an environment variable

            Returns: The OIDC URL for Azure Devops
        """
        return os.environ.get("SYSTEM_OIDCREQUESTURI")
