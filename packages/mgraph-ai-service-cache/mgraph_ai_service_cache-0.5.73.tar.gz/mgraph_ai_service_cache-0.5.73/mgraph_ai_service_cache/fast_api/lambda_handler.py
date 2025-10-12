import os

if os.getenv('AWS_REGION'):  # only execute if we are not running inside an AWS Lambda function

    from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies       # using the lightweight file (which only has the boto3 calls required to load_dependencies)
    from mgraph_ai_service_cache.config      import LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

    load_dependencies(LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS)

    def clear_osbot_modules():                            # todo: add this to load_dependencies method, since after it runs we don't need the osbot_aws.aws.lambda_.boto3__lambda
        import sys
        for module in list(sys.modules):
            if module.startswith('osbot_aws'):
                del sys.modules[module]

    clear_osbot_modules()

error   = None          # pin these variables
handler = None
app     = None
try:
    from mgraph_ai_service_cache.fast_api.Service__Fast_API import Service__Fast_API

    with Service__Fast_API() as _:
        _.setup()
        handler = _.handler()
        app     = _.app()
except Exception as exc:
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME") is None:       # raise exception when not running inside a lambda function
        raise RuntimeError(error)
    error = (f"CRITICAL ERROR: Failed to start service with:\n\n"
             f"{type(exc).__name__}: {exc}")

def run(event, context=None):
    if error:
        return error
    return handler(event, context)
