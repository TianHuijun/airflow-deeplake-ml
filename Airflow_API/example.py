import uuid

import airflow_client.client
try:
    # If you have rich installed, you will have nice colored output of the API responses
    from rich import print
except ImportError:
    print("Output will not be colored. Please install rich to get colored output: `pip install rich`")
    pass
from airflow_client.client.api import config_api, dag_api, dag_run_api
from airflow_client.client.model.dag_run import DAGRun

# The client must use the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.
#
# In case of the basic authentication below, make sure that Airflow is
# configured also with the basic_auth as backend additionally to regular session backend needed
# by the UI. In the `[api]` section of your `airflow.cfg` set:
#
# auth_backend = airflow.api.auth.backend.session,airflow.api.auth.backend.basic_auth
#
# Make sure that your user/name are configured properly - using the user/password that has admin
# privileges in Airflow

# Configure HTTP basic authorization: Basic
configuration = airflow_client.client.Configuration(
    host="http://localhost:8080/api/v1",
    username='airflow',
    password='airflow'
)

# Make sure in the [core] section, the  `load_examples` config is set to True in your airflow.cfg
# or AIRFLOW__CORE__LOAD_EXAMPLES environment variable set to True
DAG_ID = "convert_to_deeplake"

# Enter a context with an instance of the API client
with airflow_client.client.ApiClient(configuration) as api_client:

    errors = False

    print('[blue]Getting DAG list')
    dag_api_instance = dag_api.DAGApi(api_client)
    try:
        api_response = dag_api_instance.get_dags()
        print(api_response)
    except airflow_client.client.OpenApiException as e:
        print("[red]Exception when calling DagAPI->get_dags: %s\n" % e)
        errors = True
    else:
        print('[green]Getting DAG list successful')


    print('[blue]Getting Tasks for a DAG')
    try:
        api_response = dag_api_instance.get_tasks(DAG_ID)
        print(api_response)
    except airflow_client.client.exceptions.OpenApiException as e:
        print("[red]Exception when calling DagAPI->get_tasks: %s\n" % e)
        errors = True
    else:
        print('[green]Getting Tasks successful')


    print('[blue]Triggering a DAG run')
    dag_run_api_instance = dag_run_api.DAGRunApi(api_client)
    try:
        # Create a DAGRun object (no dag_id should be specified because it is read-only property of DAGRun)
        # dag_run id is generated randomly to allow multiple executions of the script
        dag_run = DAGRun(
            dag_run_id='some_test_run_' + uuid.uuid4().hex,
        )
        api_response = dag_run_api_instance.post_dag_run(DAG_ID, dag_run)
        print(api_response)
    except airflow_client.client.exceptions.OpenApiException as e:
        print("[red]Exception when calling DAGRunAPI->post_dag_run: %s\n" % e)
        errors = True
    else:
        print('[green]Posting DAG Run successful')

    # Get current configuration. Note, this is disabled by default with most installation.
    # You need to set `expose_config = True` in Airflow configuration in order to retrieve configuration.
    conf_api_instance = config_api.ConfigApi(api_client)
    try:
        api_response = conf_api_instance.get_config()
        print(api_response)
    except airflow_client.client.OpenApiException as e:
        print("[red]Exception when calling ConfigApi->get_config: %s\n" % e)
        errors = True
    else:
        print('[green]Config retrieved successfully')

    if errors:
        print ('\n[red]There were errors while running the script - see above for details')
    else:
        print ('\n[green]Everything went well')