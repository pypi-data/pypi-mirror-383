from rfctl.awslocal import lambda_command
from rfctl.common import reduce_event_source, event_arns
from typing import List
import click
import json


@click.command()
@click.pass_context
def update_config_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Updating config for function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    environment = []
    environment_spec: dict = funcdef["spec"].get("environment", {})
    for env, value in environment_spec.items():
        environment.append("{}={}".format(env, value))
    lambda_args = ["update-function-configuration",
                   "--function-name", funcdef["metadata"]["name"],
                   "--handler", funcdef["spec"]["handler"],
                   "--runtime", funcdef["spec"]["runtime"],
                   "--timeout", funcdef["spec"]["timeout"]]
    if environment:
        lambda_args.extend(["--environment", '''Variables={%s}''' % ",".join(environment)])
    lambda_command(ctx.obj["endpoint"], lambda_args)
    # concurrency
    concurrency = funcdef["spec"].get("concurrency", 1)
    lambda_args = ["put-function-concurrency",
                   "--function-name", funcdef["metadata"]["name"],
                   "--reserved-concurrent-executions", concurrency]
    lambda_command(ctx.obj["endpoint"], lambda_args)
    # events
    current_events: List[dict] = []
    for arn in event_arns:
        lambda_args = ["list-event-source-mappings",
                       "--function-name", funcdef["metadata"]["name"],
                       "--event-source-arn", arn]
        bts = lambda_command(ctx.obj["endpoint"], lambda_args, fetch_out=True)
        aws_rsp: dict = json.loads(bts)
        current_events.extend(aws_rsp.get("EventSourceMappings", []))
    for event in current_events:
        lambda_args = ["delete-event-source-mapping",
                       "--uuid", event.get("UUID")]
        lambda_command(ctx.obj["endpoint"], lambda_args, fetch_out=True)
    if funcdef["spec"].get("events"):
        for event in funcdef["spec"].get("events"):
            event_source_arn = "arn:{}:{}".format(event["type"], event["name"])
            self_managed_event_source = reduce_event_source(event)
            lambda_args = ["create-event-source-mapping",
                           "--function-name", funcdef["metadata"]["name"],
                           "--event-source-arn", event_source_arn,
                           "--self-managed-event-source", self_managed_event_source]
            lambda_command(ctx.obj["endpoint"], lambda_args)
