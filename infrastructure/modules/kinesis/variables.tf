variable "stream_name" {
  description = "The Kinesis stream name"
  default     = "ride_events"
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

variable "shard_level_metrics" {
  description = "The Kinesis stream shard level metrics"
  default     = ["IncomingBytes", "OutgoingBytes"]
  type        = list(string)
}

variable "stream_mode_details" {
  description = "The Kinesis stream mode details"
  default     = "PROVISIONED"
  type        = string
}

variable "tags" {
  description = "The Kinesis stream tags"
  default     = "Chinedu Ezeofor"
  type        = string
}
