resource "aws_ecs_cluster" "ecs_cluster" {
  name = "my-ecs-cluster"
}

resource "aws_ecs_capacity_provider" "ecs_capacity_provider" {
  name = "test1"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.ecs_asg.arn

    managed_scaling {
      maximum_scaling_step_size = 1000
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 3
    }
  }
}


resource "aws_ecs_cluster_capacity_providers" "ecs_cluster_capacity_providers" {
  cluster_name       = aws_ecs_cluster.ecs_cluster.name
  capacity_providers = [aws_ecs_capacity_provider.ecs_capacity_provider.name]
  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.ecs_capacity_provider.name
  }
}

resource "aws_ecs_task_definition" "ecs_task_definition" {
  family             = "my-ecs-task"
  network_mode       = "awsvpc"
  execution_role_arn = "arn:aws:iam::532199187081:role/ecsTaskExecutionRole"
  cpu                = 2048
  memory             = 2048

  container_definitions = jsonencode([
    {
      name      = "django-app-conatiner"
      image     = "${aws_ecr_repository.django_repository.repository_url}:latest",
                  # 348949640551.dkr.ecr.ap-south-1.amazonaws.com/django-app

      cpu       = 1024
      memory    = 1024
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      depends_on = [
        {
          containerName = "mysql-db-repo"
          condition     = "START"
        }
      ]
      mountPoints = [
        {
          sourceVolume  = "spam_mysql_db"
          containerPath = "/var/lib/mysql"
          readOnly      = false
        }
      ]
    },
    {
      name      = "mysql-db-repo"
      image     = "348949640551.dkr.ecr.ap-south-1.amazonaws.com/mysql-db-repo:"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 3307
          hostPort      = 3306
          protocol      = "tcp"
        }
      ]
      volumes = [
        {
          name       = "spam_mysql_db"
          hostPath   = "/path/to/host/volume"
          dockerPath = "/var/lib/mysql"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "ecs_service" {
  name            = "my-ecs-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task_definition.arn
  desired_count   = 2

  network_configuration {
    subnets         = [aws_subnet.subnet1.id, aws_subnet.subnet2.id]
    security_groups = [aws_security_group.security_group.id]
  }

  force_new_deployment = true
  placement_constraints {
    type = "distinctInstance"
  }

  triggers = {
    redeployment = timestamp()
  }

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.ecs_capacity_provider.name
    weight            = 100
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "django-app"
    container_port   = 8000
  }
  depends_on = [aws_autoscaling_group.ecs_asg]
}