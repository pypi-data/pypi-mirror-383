from aws_lambda_builders.builder import LambdaBuilder
from aws_lambda_builders.architecture import X86_64
import traceback
import tempfile
import zipfile
import click
import os
import re


def get_dependency_manager(lang: str):
    if "python" in lang:
        return "pip"
    if "go" in lang:
        return "modules"
    raise Exception("not support language %s" % lang)


def get_runtime(runtime: str):
    match = None
    if "golang" in runtime:
        pattern = r'go1\.x'
        match = re.search(pattern, runtime.replace("golang", "go"))
    if "python" in runtime:
        pattern = r'python\d\.\d+'
        match = re.search(pattern, runtime)
    if not match:
        raise Exception("not support runtime {}".format(runtime))
    return match.group(0)


@click.command()
@click.option('--out', default=os.path.join(os.getcwd(), "lambda.zip"), type=click.Path(exists=False, dir_okay=False, resolve_path=True))
@click.pass_context
def build_command(ctx: click.Context, out: str):
    do_build(ctx, out)


def do_build(ctx: click.Context, out: str) -> bool:
    funcdef = ctx.obj["funcdef"]
    build: dict = funcdef["spec"]["build"]
    capabilities = {
        "language": build["language"],
        "dependency_manager": get_dependency_manager(build["language"])
    }
    envs: dict = build.get("environment", {})
    os.environ.update(envs)
    with tempfile.TemporaryDirectory() as tmp_dir:
        click.echo("Building function %s/%s in temporary directory %s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"], tmp_dir))
        try:
            runtime = get_runtime(funcdef["spec"]["runtime"])
            click.echo("Building function %s/%s with builder runtime %s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"], runtime))
            params = {
                "source_dir": build["source"],
                "artifacts_dir": os.path.join(tmp_dir, "lambda"),
                "scratch_dir": os.path.join(tmp_dir, "tmp"),
                "manifest_path": os.path.join(build["source"], build["manifest"]),
                "architecture": build["architecture"],
                "runtime": runtime,
                "optimizations": {},
                "options": {
                    "artifact_executable_name": funcdef["spec"]["handler"],
                }
            }
            builder = LambdaBuilder(
                language=capabilities["language"],
                dependency_manager=capabilities["dependency_manager"],
                application_framework=None,
            )
            builder.build(
                params["source_dir"],
                params["artifacts_dir"],
                params["scratch_dir"],
                params["manifest_path"],
                executable_search_paths=params.get("executable_search_paths", None),
                runtime=params["runtime"],
                optimizations=params["optimizations"],
                options=params["options"],
                mode=params.get("mode", None),
                download_dependencies=params.get("download_dependencies", True),
                dependencies_dir=params.get("dependencies_dir", None),
                combine_dependencies=params.get("combine_dependencies", True),
                architecture=params.get("architecture", X86_64),
                is_building_layer=params.get("is_building_layer", False),
                experimental_flags=params.get("experimental_flags", []),
                build_in_source=params.get("build_in_source", None),
            )
            click.echo("Packaging function %s/%s to %s" % (funcdef["metadata"]["namespace"], funcdef["metadata"]["name"], out))
            if os.path.isfile(out):
                os.remove(out)
            with zipfile.ZipFile(out, mode='w') as zip_file:
                directory = os.path.join(tmp_dir, "lambda")
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, os.path.relpath(file_path, directory))
            ctx.obj["out"] = out
            return True
        except Exception as ex:
            click.echo("Build error:\n %s" % traceback.format_exc())
            return False
