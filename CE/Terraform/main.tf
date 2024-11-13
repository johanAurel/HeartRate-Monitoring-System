provider "aws" {
  region     = "eu-west-2"
  access_key = var.aws_access_key  # Ensure this variable is defined in variables.tf or environment
  secret_key = var.aws_secret_key  # Ensure this variable is defined in variables.tf or environment
}

# VPC
resource "aws_vpc" "django_vpc" {
  cidr_block = "10.0.0.0/16"  # Ensure your CIDR block is within the valid range
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

# Internet Gateway for VPC
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.django_vpc.id

  tags = {
    Name = "internet_gateway"
  }
}

# Private Route Table with NAT Gateway
resource "aws_route_table" "django_route_table" {
  vpc_id = aws_vpc.django_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "django_route_table"
  }
}


resource "aws_subnet" "django_subnet" {
  count = 2

  vpc_id                  = aws_vpc.django_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"  
  availability_zone       = element(var.aws_availability_zones, count.index)
  map_public_ip_on_launch = true

  tags = {
    Name = "Django Subnet ${count.index + 1}"
  }
}

resource "aws_route_table_association" "private_subnet_association" {
  count          = 2
  subnet_id      = aws_subnet.django_subnet[count.index].id
  route_table_id = aws_route_table.django_route_table.id
}

# RDS Subnet Group
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "db-subnet-group"
  subnet_ids = [aws_subnet.django_subnet[0].id, aws_subnet.django_subnet[1].id]
  tags = {
    Name = "RDS subnet group"
  }
}

//variable "my_ip" {}//run export TF_VAR_my_ip="$(curl -4 ifconfig.me)/32" to get your ipv4 on bash


# Update Security Group to allow inbound traffic on port 5432 for private subnet resources
resource "aws_security_group" "allow_postgres" {
  name        = "allow_postgres"
  description = "Allow inbound PostgreSQL traffic"
  vpc_id      = aws_vpc.django_vpc.id

  # Allow inbound PostgreSQL traffic on port 5432 from your IP
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Ensure my_ip is in correct CIDR format
  }

  # Allow all outbound traffic from this security group
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
     Name = "allow_all"
  }
}

resource "aws_db_instance" "heartbeat_rds" {
  allocated_storage       = 20
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "16.3"
  instance_class          = "db.t3.micro"
  identifier              = "my-django-rds"
  db_name                 = "heartbeat_monitor"
  username                = var.user
  password                = var.db_password
  skip_final_snapshot     = true
  publicly_accessible     = true
  vpc_security_group_ids  = [aws_security_group.allow_postgres.id]
  db_subnet_group_name    = aws_db_subnet_group.db_subnet_group.name
  multi_az = false
}

# IAM Role for Lambda (if not already created)
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect    = "Allow"
        Sid       = ""
      }
    ]
  })
}

# IAM Role Policy (Permissions for Lambda to interact with IoT and RDS)
resource "aws_iam_role_policy" "lambda_exec_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = [
          "iot:Publish",
          "iot:Connect",
          "iot:Receive",
          "iot:Subscribe"
        ]
        Effect    = "Allow"
        Resource  = "*"
      },
      {
        Action    = [
          "rds:ExecuteStatement",
          "rds:BatchExecuteStatement",
          "rds:DescribeDBInstances"
        ]
        Effect    = "Allow"
        Resource  = "*"
      },
      {
        Action    = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect    = "Allow"
        Resource  = "*"
      }
    ]
  })
}


# Lambda Function (Replace with your existing Lambda resource or ARN)
resource "aws_lambda_function" "lambda" {
  function_name = "HeartbeatLambda"

  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index.handler"  # Ensure this is your Lambda handler
  runtime       = "nodejs20.x"     # Replace with your Lambda runtime
  filename      = "./lambda/lambda_function.zip"     # Replace with the path to your zipped Lambda code
  vpc_config {
    # Every subnet should be able to reach an EFS mount target in the same Availability Zone. Cross-AZ mounts are not permitted.
    subnet_ids         = [aws_subnet.django_subnet[0].id,aws_subnet.django_subnet[1].id]
    security_group_ids = [aws_security_group.allow_postgres.id]
  }

}

# IoT Rule that listens to the MQTT topic 'devices/+/heartbeat'
# IoT Rule that listens to the MQTT topic 'devices/+/heartbeat'
resource "aws_iot_topic_rule" "heartbeat_rule" {
  name        = "HeartbeatRule"
  description = "Triggers Lambda function when heartbeat message is received"

  sql         = "SELECT * FROM 'sdk/test/python'"  # Topic filter
  sql_version = "2016-03-23"

  # Action: Invoke Lambda function
  lambda {
    function_arn = aws_lambda_function.lambda.arn
  }

  # Ensure the rule is enabled
  enabled = true
}

# Grant IoT permission to invoke the Lambda function
resource "aws_lambda_permission" "allow_iot_invoke" {
  statement_id  = "AllowIoTInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.heartbeat_rule.arn
}