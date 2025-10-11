from rfctl.awslocal import lambda_command
import click


@click.command()
@click.pass_context
def delete_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Deleting function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    lambda_args = ["delete-function",
                   "--function-name", funcdef["metadata"]["name"]]
    lambda_command(ctx.obj["endpoint"], lambda_args)
