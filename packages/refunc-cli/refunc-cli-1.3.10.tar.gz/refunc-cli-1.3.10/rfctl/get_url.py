from rfctl.awslocal import lambda_command
import click


@click.command()
@click.pass_context
def get_url_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Get function url %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    lambda_args = ["get-function-url-config",
                   "--function-name", funcdef["metadata"]["name"]]
    lambda_command(ctx.obj["endpoint"], lambda_args)
