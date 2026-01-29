terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstate29012026"
    container_name       = "tfstate"
    key                  = "openshift-rag-demo.tfstate"
  }
}