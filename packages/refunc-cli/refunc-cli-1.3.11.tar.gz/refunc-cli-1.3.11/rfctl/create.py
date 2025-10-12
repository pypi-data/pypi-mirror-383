from rfctl.awslocal import lambda_command
from rfctl.build import do_build
from rfctl.common import reduce_event_source, encode_base64
import click
import os
import atexit


@click.command()
@click.pass_context
def create_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    out = os.path.join(ctx.obj["working_dir"], "lambda.zip")

    def cleanup():
        os.remove(out)
    atexit.register(cleanup)
    if not do_build(ctx, out):
        return
    click.echo("Creating function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    environment = []
    environment_spec: dict = funcdef["spec"].get("environment", {})
    for env, value in environment_spec.items():
        environment.append("{}={}".format(env, value))
    lambda_args = ["create-function",
                   "--function-name", funcdef["metadata"]["name"],
                   "--handler", funcdef["spec"]["handler"],
                   "--zip-file", "fileb://{}".format(out),
                   "--runtime", funcdef["spec"]["runtime"],
                   "--timeout", funcdef["spec"]["timeout"]]
    if funcdef["spec"].get("description"):
        lambda_args.extend(["--description", encode_base64(funcdef["spec"].get("description"))])
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
    if funcdef["spec"].get("events"):
        for event in funcdef["spec"].get("events"):
            event_source_arn = "arn:{}:{}".format(event["type"], event["name"])
            self_managed_event_source = reduce_event_source(event)
            lambda_args = ["create-event-source-mapping",
                           "--function-name", funcdef["metadata"]["name"],
                           "--event-source-arn", event_source_arn,
                           "--self-managed-event-source", self_managed_event_source]
            lambda_command(ctx.obj["endpoint"], lambda_args)
