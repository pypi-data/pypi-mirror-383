import os
import sys
import subprocess
import six
from threading import Thread
from io import BytesIO


def to_str(s):
    if six.PY3 and not isinstance(s, six.string_types):
        s = s.decode('utf-8')
    return s


def run(cmd, env, fetch_out=False):
    out_io = BytesIO()

    def output_reader(pipe, out):
        with pipe:
            for line in iter(pipe.readline, b''):
                if fetch_out:
                    out.write(line)
                    continue
                line = to_str(line)
                out.write(line)
                out.flush()
    str_cmd = " ".join(cmd)
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=env)
    if fetch_out:
        Thread(target=output_reader, args=[process.stdout, out_io]).start()
        Thread(target=output_reader, args=[process.stderr, out_io]).start()
    else:
        Thread(target=output_reader, args=[process.stdout, sys.stdout]).start()
        Thread(target=output_reader, args=[process.stderr, sys.stderr]).start()

    rc = process.wait()
    if rc != 0:
        print("The follow cmd exec error:")
        print("{}".format(str_cmd))
        sys.exit(rc)

    out_io.seek(0)
    return out_io.read()


def lambda_command(endpoint_url, args, fetch_out=False):
    # prepare cmd args
    cmd_args = ["aws", "--no-verify-ssl", "--endpoint-url", endpoint_url, "lambda"]
    cmd_args.extend([str(x) for x in args])
    role = False
    for param in args:
        if param == "create-function":
            role = True
    if role:
        cmd_args.append("--role")
        cmd_args.append("")
    # prepare env vars
    env_dict = os.environ.copy()
    env_dict['PYTHONWARNINGS'] = os.environ.get('PYTHONWARNINGS', 'ignore:Unverified HTTPS request')
    env_dict['AWS_DEFAULT_REGION'] = os.environ.get('AWS_DEFAULT_REGION', '')
    env_dict['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID', '_not_needed_locally_')
    env_dict['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY', '_not_needed_locally_')
    # run the command
    return run(cmd_args, env_dict, fetch_out)
