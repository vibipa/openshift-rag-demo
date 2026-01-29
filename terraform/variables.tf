variable "project_name" {
  description = "Project name"
  type        = string
  default     = "openshift-rag-demo"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "canadacentral"
}

variable "use_free_tier" {
  description = "Use free tier for AI Search"
  type        = bool
  default     = true
}