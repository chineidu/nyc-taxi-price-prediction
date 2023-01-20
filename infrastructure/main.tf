# Configure State: Create a state bucket in AWS beforehand
terraform {
  required_version = "~> 4.0"
  backend "s3" {
    bucket  = "mlops-tf-state-neidu"
    key     = "mlops-project-stg.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

# Used to get the access to the Account ID, User ID, and ARN in which
# Terraform is authorized.
data "aws_caller_identity" "current_identity" {}

# A local value assigns a name to an expression, so you can use the name
# multiple times within a module instead of repeating the expression.
locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}
