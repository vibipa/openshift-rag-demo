resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_resource_group" "demo" {
  name     = "openshift-rag-demo-rg"
  location = "var.location"
  
  tags = {
    Project     = "OpenShift-RAG-Demo"
    ManagedBy   = "Terraform"
    Owner       = "Vibi Abraham"
  }
}