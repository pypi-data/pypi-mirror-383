from rfctl.awslocal import lambda_command
from rfctl.common import reduce_url_cors
import click


@click.command()
@click.pass_context
def create_url_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    click.echo("Creating url for function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    lambda_args = ["create-function-url-config",
                   "--function-name", funcdef["metadata"]["name"],
                   "--auth-type", "None"]
    if funcdef["spec"].get("url", {}).get("cors"):
        lambda_args.extend(["--cors", reduce_url_cors(funcdef["spec"]["url"]["cors"])])
    lambda_command(ctx.obj["endpoint"], lambda_args)
