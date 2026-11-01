terraform {
  required_version = ">= 1.5.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

variable "replicas" {
  description = "Number of nginx demo containers"
  type        = number
  default     = 2
  validation {
    condition     = var.replicas >= 1 && var.replicas <= 10 && floor(var.replicas) == var.replicas
    error_message = "Choose a whole number of replicas from 1 to 10."
  }
}

resource "docker_image" "web" {
  name         = "nginx:alpine"
  keep_locally = true
}

resource "docker_container" "web" {
  count = var.replicas
  name  = "rishav-lab3-web-${count.index + 1}"
  image = docker_image.web.image_id
  ports {
    internal = 80
    external = 8082 + count.index
    ip       = "127.0.0.1"
  }
  upload {
    content = "<h1>Rishav - DevOps Lab 3</h1><p>Roll no. 2301730245 | Replica ${count.index + 1}</p>"
    file    = "/usr/share/nginx/html/index.html"
  }
}

output "urls" {
  value = [for container in docker_container.web : "http://localhost:${container.ports[0].external}"]
}
