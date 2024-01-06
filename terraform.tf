# terraform {
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 5.0"
#     }
#   }
# }

# # Define AWS provider
# provider "aws" {
#   region = "ap-south-1"
# }


# # Create ECR repository for Django web application
# resource "aws_ecr_repository" "django_repository" {
#   name = "django-webapp-repo"
#   encryption_configuration {
#     encryption_type = "AES256"
#   }
# }

# # Create ECR repository for MySQL
# resource "aws_ecr_repository" "mysql_repository" {
#   name = "mysql-repo"
#   encryption_configuration {
#     encryption_type = "AES256"
#   }
# }



# # Create ECS cluster
# resource "aws_ecs_cluster" "my_cluster" {
#   name = "bhavin-ecs-cluster"
# }

# # Create ECR lifecycle policy for Django repository
# resource "aws_ecr_lifecycle_policy" "django_lifecycle_policy" {
#   repository = aws_ecr_repository.django_repository.name

#   policy = <<EOF
# {
#   "rules": [
#     {
#       "rulePriority": 1,
#       "description": "Expire images older than 2 days",
#       "selection": {
#         "tagStatus": "any",
#         "countType": "sinceImagePushed",
#         "countUnit": "days",
#         "countNumber": 2
#       },
#       "action": {
#         "type": "expire"
#       }
#     }
#   ]
# }
# EOF
# }

# # Create ECR lifecycle policy for MySQL repository
# resource "aws_ecr_lifecycle_policy" "mysql_lifecycle_policy" {
#   repository = aws_ecr_repository.mysql_repository.name

#   policy = <<EOF
# {
#   "rules": [
#     {
#       "rulePriority": 1,
#       "description": "Expire images older than 2 days",
#       "selection": {
#         "tagStatus": "any",
#         "countType": "sinceImagePushed",
#         "countUnit": "days",
#         "countNumber": 2
#       },
#       "action": {
#         "type": "expire"
#       }
#     }
#   ]
# }
# EOF
# }

# # Create IAM role for ECS task execution
# resource "aws_iam_role" "ecs_task_execution_role" {
#   name = "ecs-task-execution-role"

#   assume_role_policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Principal": {
#         "Service": "ecs-tasks.amazonaws.com"
#       },
#       "Action": "sts:AssumeRole"
#     }
#   ]
# }
# EOF
# }

# # Attach policies to the ECS task execution role
# resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_attachment" {
#   role       = aws_iam_role.ecs_task_execution_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
# }

# # Create security group for ECS tasks
# resource "aws_security_group" "ecs_task_security_group" {
#   name        = "ecs-task-security-group"
#   description = "Security group for ECS tasks"

#   ingress {
#     from_port   = 0
#     to_port     = 65535
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # Create IAM role for ECS task
# resource "aws_iam_role" "ecs_task_role" {
#   name               = "ecs-task-role"
#   assume_role_policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Principal": {
#         "Service": "ecs-tasks.amazonaws.com"
#       },
#       "Action": "sts:AssumeRole"
#     }
#   ]
# }
# EOF
# }

# # Attach policies to the ECS task role
# resource "aws_iam_role_policy_attachment" "ecs_task_role_policy_attachment" {
#   role       = aws_iam_role.ecs_task_role.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
# }

# # Create Application Load Balancer
# resource "aws_lb" "django_load_balancer" {
#   name               = "django-load-balancer"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.ecs_task_security_group.id]
#   subnets            = ["subnet-12345678", "subnet-87654321"] # Replace with your subnet IDs
# }

# # Create Target Group
# resource "aws_lb_target_group" "django_target_group" {
#   name     = "django-target-group"
#   port     = 8000
#   protocol = "HTTP"
#   vpc_id   = "vpc-12345678" # Replace with your VPC ID
# }

# # Create Listener
# resource "aws_lb_listener" "django_listener" {
#   load_balancer_arn = aws_lb.django_load_balancer.arn
#   port              = 80
#   protocol          = "HTTP"

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.django_target_group.arn
#   }
# }

# # Create ECS task definition and service for Django web application
# resource "aws_ecs_task_definition" "django_task_definition" {
#   family                = "django-task-definition"
#   container_definitions = <<DEFINITION
# [
#   {
#     "name": "django-container",
#     "image": "${aws_ecr_repository.django_repository.repository_url}:latest",
#     "portMappings": [
#       {
#         "containerPort": 8000,
#         "hostPort": 8000,
#         "protocol": "tcp"
#       }
#     ],
#     "command": ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"],
#     "logConfiguration": {
#       "logDriver": "awslogs",
#       "options": {
#         "awslogs-group": "/ecs/django-container",
#         "awslogs-region": "us-west-2",
#         "awslogs-stream-prefix": "ecs"
#       }
#     }
#   },
#   {
#     "name": "mysql-container",
#     "image": "${aws_ecr_repository.mysql_repository.repository_url}:latest",
#     "portMappings": [
#       {
#         "containerPort": 3307,
#         "hostPort": 3306,
#         "protocol": "tcp"
#       }
#     ],
#     "volumes": [
#       {
#         "name": "mysql-data",
#         "dockerVolumeConfiguration": {
#           "scope": "shared",
#           "autoprovision": true,
#           "driver": "local",
#           "driverOpts": {
#             "type": "nfs",
#             "device": ":/path/to/mysql-data"
#           }
#         }
#       }
#     ]
#   }
# ]
# DEFINITION
#   execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
#   task_role_arn      = aws_iam_role.ecs_task_role.arn
# }

# # Create ECS service for Django web application
# resource "aws_ecs_service" "django_service" {
#   name            = "django-service"
#   cluster         = aws_ecs_cluster.my_cluster.id
#   task_definition = aws_ecs_task_definition.django_task_definition.arn
#   desired_count   = 2

#   deployment_controller {
#     type = "CODE_DEPLOY"
#   }

#   load_balancer {
#     target_group_arn = aws_lb_target_group.django_target_group.arn
#     container_name   = "django-container"
#     container_port   = 8000
#   }
# }

# # Create ECS service for MySQL
# resource "aws_ecs_service" "mysql_service" {
#   name            = "mysql-service"
#   cluster         = aws_ecs_cluster.my_cluster.id
#   task_definition = aws_ecs_task_definition.django_task_definition.arn
#   desired_count   = 1
# }
