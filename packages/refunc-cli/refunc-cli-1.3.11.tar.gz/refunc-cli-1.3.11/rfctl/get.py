from rfctl.awslocal import lambda_command
from rfctl.common import event_arns
import click


@click.command()
@click.pass_context
def get_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Get function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    lambda_args = ["get-function",
                   "--function-name", funcdef["metadata"]["name"]]
    lambda_command(ctx.obj["endpoint"], lambda_args)
    # events
    for arn in event_arns:
        lambda_args = ["list-event-source-mappings",
                       "--function-name", funcdef["metadata"]["name"],
                       "--event-source-arn", arn]
        lambda_command(ctx.obj["endpoint"], lambda_args)
