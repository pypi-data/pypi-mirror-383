
python_source = {
    "main.py": """
def lambda_handler(event,ctx):
    return {
        "msg":"hello"
    }
""",
    "test.py": """
from rfctl.client import LambdaClient

client = LambdaClient("{namespace}")

rsp = client.invoke_function("{name}", {}, get_log=True)

print(rsp)
""",
    "requirements.txt": """""",
}

golang_source = {
    "handler.go": """
package main

import (
	"context"

	"github.com/aws/aws-lambda-go/lambda"
)

type Event struct{}

func HandleRequest(ctx context.Context, event Event) (string, error) {
	return "hello", nil
}

func main() {
	lambda.Start(HandleRequest)
}

""",
    "go.mod": """
module main

go 1.18

require github.com/aws/aws-lambda-go v1.40.0

""",
    "go.sum": """
github.com/aws/aws-lambda-go v1.40.0 h1:6dKcDpXsTpapfCFF6Debng6CiV/Z3sNHekM6bwhI2J0=
github.com/aws/aws-lambda-go v1.40.0/go.mod h1:jwFe2KmMsHmffA1X2R09hH6lFzJQxzI8qK17ewzbQMM=
github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
github.com/stretchr/testify v1.7.2 h1:4jaiDzPyXQvSd7D0EjG45355tLlV3VOECpq10pLC+8s=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=

""",
    "test.py": """
from rfctl.client import LambdaClient

client = LambdaClient("{namespace}")

rsp = client.invoke_function("{name}", {}, get_log=True)

print(rsp)
""",
}

sources = {
    "python": python_source,
    "go": golang_source
}
