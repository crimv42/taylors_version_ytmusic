# This is required to get the AWS region via ${data.aws_region.current}.
data "aws_region" "current" {
}

# Define a Lambda function.
#
# The handler is the name of the executable for python3.10 runtime.
resource "aws_lambda_function" "taylors_version" {
  function_name    = "taylors_version"
  filename         = "tv.zip"
  handler          = "fusb"
  source_code_hash = sha256(filebase64("tv.zip"))
  role             = aws_iam_role.taylors_version_role.arn
  runtime          = "python3.10"
  memory_size      = 128
  timeout          = 1
}

# A Lambda function may access to other AWS resources such as S3 bucket. So an
# IAM role needs to be defined.
#
# The date 2012-10-17 is just the version of the policy language used here [1].
#
# [1]: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_version.html
resource "aws_iam_role" "taylors_version_role" {
  name               = "taylors_version_role"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": {
    "Action": "sts:AssumeRole",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Effect": "Allow"
  }
}
POLICY
}

# Allow API gateway to invoke the taylors_version Lambda function.
resource "aws_lambda_permission" "taylors_version_perms" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.taylors_version.arn
  principal     = "apigateway.amazonaws.com"
}

# A Lambda function is not a usual public REST API. We need to use AWS API
# Gateway to map a Lambda function to an HTTP endpoint.
resource "aws_api_gateway_resource" "taylors_version_gateway" {
  rest_api_id = aws_api_gateway_rest_api.taylors_version_api.id
  parent_id   = aws_api_gateway_rest_api.taylors_version_api.root_resource_id
  path_part   = "fusb"
}

resource "aws_api_gateway_rest_api" "taylors_version_api" {
  name = "taylors_version_api"
}

#           GET
# Internet -----> API Gateway
resource "aws_api_gateway_method" "taylors_version_api_get" {
  rest_api_id   = aws_api_gateway_rest_api.taylors_version_api.id
  resource_id   = aws_api_gateway_resource.taylors_version_gateway.id
  http_method   = "GET"
  authorization = "NONE"
}

#              POST
# API Gateway ------> Lambda
# For Lambda the method is always POST and the type is always AWS_PROXY.
#
# The date 2015-03-31 in the URI is just the version of AWS Lambda.
resource "aws_api_gateway_integration" "taylors_version_gateway_integration" {
  rest_api_id             = aws_api_gateway_rest_api.taylors_version_api.id
  resource_id             = aws_api_gateway_resource.taylors_version_gateway.id
  http_method             = aws_api_gateway_method.taylors_version_api_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${aws_lambda_function.taylors_version.arn}/invocations"
}

# This resource defines the URL of the API Gateway.
resource "aws_api_gateway_deployment" "taylors_version_v1" {
  depends_on = [
    "aws_api_gateway_integration.taylors_version_gateway_integration"
  ]
  rest_api_id = aws_api_gateway_rest_api.taylors_version_api.id
  stage_name  = "v1"
}

# Set the generated URL as an output. Run `terraform output url` to get this.
output "url" {
  value = "${aws_api_gateway_deployment.taylors_version_v1.invoke_url}${aws_api_gateway_resource.taylors_version_gateway.path}"
}
