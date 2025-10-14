from collections import OrderedDict
from rfctl.init_source import sources
import click
import os
import sys

template = """metadata:
  name: {name}
  namespace: {namespace}
spec:
  build:
    source: .
    manifest: {manifest}
    language: {language}
    architecture: x86_64
  handler: {handler}
  timeout: 120
  runtime: "{runtime}"
  concurrency: 1
  environment:
    ENV_TEST: TEST
#  url:
#    cors:
#      allowCredentials: true
#      allowHeaders: "*"
#      allowMethods: "*"
#      allowOrigins: "*"
#      exposeHeaders: "*"
#      maxAge: 300
#  events:
#    - name: hourly
#      type: cron
#      mapping:
#        cron: 0 * * * *
#        location: Asia/Shanghai
#        args:
#          var1: value1
#        saveLog: false
#        saveResult: false
#    - name: mcp
#      type: mcp
#      mapping:
#        args:
#          token: mcp-token-secret-name
#          tools:
#            - name: echo-hello
#              desc: Func MCP Tool Description
#              schema:
#                type: object
#                properties: {{}}
#                required: []
#        saveLog: false
#        saveResult: false
"""


@click.command()
@click.pass_context
def init_command(ctx: click.Context):
    funcdef = ctx.obj["manifest"]
    click.echo("Initing function manifest in %s" % funcdef)
    name = read_user_variable("Name", None)
    namespace = read_user_variable("Namespace", None)
    language = read_user_choice("Language", ["python", "go"])
    runtime, manifest = None, None
    handler = ""
    if language == "python":
        runtime = read_user_choice("Runtime", ["python3.10", "python3.9", "python3.8"])
        manifest = "requirements.txt"
        handler = "main.lambda_handler"
    if language == "go":
        runtime = "golang1.x"
        manifest = "go.mod"
        handler = "handler"
    content = template.format(**{"name": name, "namespace": namespace, "manifest": manifest,
                              "language": language, "handler": handler, "runtime": runtime})
    if not os.path.exists(funcdef):
        with open(funcdef, 'w', encoding="utf-8") as f:
            f.write(content)
    else:
        click.echo("Function manifest %s exists" % funcdef)
        sys.exit(-1)
    do_init_source(language, {"name": name, "namespace": namespace})


def do_init_source(lang: str, meta: dict):
    source_items: dict = sources.get(lang)
    if not source_items:
        return
    for path, src_template in source_items.items():
        content = src_template
        for key, value in meta.items():
            content = content.replace("{%s}" % key, value)
        if not os.path.exists(path):
            with open(path, 'w', encoding="utf-8") as f:
                f.write(content)


def read_user_variable(var_name, default_value):
    """Prompt user for variable and return the entered value or given default.
    :param str var_name: Variable of the context to query the user
    :param default_value: Value that will be returned if no input happens
    """
    return click.prompt(var_name, default=default_value)


def read_user_choice(var_name, options):
    """Prompt the user to choose from several options for the given variable.
    The first item will be returned if no input happens.
    :param str var_name: Variable as specified in the context
    :param list options: Sequence of options that are available to select from
    :return: Exactly one item of ``options`` that has been chosen by the user
    """
    if not isinstance(options, list):
        raise TypeError

    if not options:
        raise ValueError

    choice_map = OrderedDict((f'{i}', value) for i, value in enumerate(options, 1))
    choices = choice_map.keys()
    default = '1'

    choice_lines = ['{} - {}'.format(*c) for c in choice_map.items()]
    prompt = '\n'.join(
        (
            f"Select {var_name}:",
            "\n".join(choice_lines),
            f"Choose from {', '.join(choices)}",
        )
    )

    user_choice = click.prompt(
        prompt, type=click.Choice(choices), default=default, show_choices=False
    )
    return choice_map[user_choice]
