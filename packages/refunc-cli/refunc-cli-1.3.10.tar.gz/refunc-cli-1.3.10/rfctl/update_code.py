from rfctl.awslocal import lambda_command
from rfctl.build import do_build
import click
import os
import atexit


@click.command()
@click.pass_context
def update_code_command(ctx: click.Context):
    funcdef = ctx.obj["funcdef"]
    out = os.path.join(ctx.obj["working_dir"], "lambda.zip")

    def cleanup():
        os.remove(out)
    atexit.register(cleanup)
    if not do_build(ctx, out):
        return
    click.echo("Updating code for function %s/%s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"]))
    lambda_args = ["update-function-code",
                   "--function-name", funcdef["metadata"]["name"],
                   "--zip-file", "fileb://{}".format(out)]
    lambda_command(ctx.obj["endpoint"], lambda_args)
