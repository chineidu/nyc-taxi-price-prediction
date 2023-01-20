variable "aws_region" {
  description = "The AWS region"
  default     = "us-east-1"
  type        = string
}

variable "source_stream_name" {
  description = "The source stream name"
  default       = "ride_events"
  type        = string
}

variable "project_name" {
  description = "The project name"
  default       = "NYC_taxi_project"
  type        = string
}

variable "shard_count" {
  description = "The Kinesis stream shard count"
  default     = 1
  type        = number
}

variable "retention_period" {
  description = "The Kinesis stream retention period"
  default     = 48
  type        = number
}
