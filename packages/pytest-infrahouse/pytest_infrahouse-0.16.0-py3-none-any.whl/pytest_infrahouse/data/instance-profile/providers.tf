provider "aws" {
  dynamic "assume_role" {
    for_each = var.role_arn != null ? [1] : []
    content {
      role_arn = var.role_arn
    }
  }
  region = var.region
  default_tags {
    tags = {
      created_by : var.calling_test
      created_by_fixture : "infrahouse/pytest-infrahouse/instance-profile"
    }

  }
}
