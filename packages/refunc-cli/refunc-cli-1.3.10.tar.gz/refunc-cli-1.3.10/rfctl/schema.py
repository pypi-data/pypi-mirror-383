from aws_lambda_builders.architecture import X86_64


def set_funcdef_defaults(funcdef: dict):
    spec: dict = funcdef.get("spec", {})
    build: dict = spec.get("build", {})
    if not build.get("architecture"):
        build["architecture"] = X86_64
    return funcdef


funcdef_schema = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "namespace": {
                    "type": "string"
                }
            },
            "required": ["name", "namespace"]
        },
        "spec": {
            "type": "object",
            "properties": {
                "build": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string"
                        },
                        "manifest": {
                            "type": "string"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["python", "go"]
                        },
                        "architecture": {
                            "type": "string",
                            "enum": [X86_64]
                        }
                    },
                    "required": ["source", "manifest", "language"]
                },
                "handler": {
                    "type": "string"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 0
                },
                "runtime": {
                    "type": "string"
                }
            },
            "required": ["build", "handler", "timeout", "runtime"]
        }
    },
    "required": ["metadata", "spec"]
}
