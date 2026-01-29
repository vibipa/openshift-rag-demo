terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstateopenshiftdemo"
    container_name       = "tfstate"
    key                  = "openshift-rag-demo.tfstate"
  }
}