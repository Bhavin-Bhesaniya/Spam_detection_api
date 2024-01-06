#!/bin/bash
# Update the instance
yum update -y

# Install Docker
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user

echo ECS_CLUSTER=my-ecs-cluster >> /etc/ecs/ecs.config

# Install and configure Nginx
amazon-linux-extras install nginx1.12 -y
cat > /etc/nginx/conf.d/default.conf <<EOF
server {
    listen 80;
    location / {
        proxy_pass http://localhost:8000;
    }
}
EOF
service nginx start