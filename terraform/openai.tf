resource "azurerm_cognitive_account" "openai" {
  name                = "openshift-demo-openai-${random_string.suffix.result}"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.demo.name
  kind                = "OpenAI"
  sku_name            = "S0"
  
  custom_subdomain_name = "openshift-demo-openai-${random_string.suffix.result}"
  public_network_access_enabled = true
  
  tags = azurerm_resource_group.demo.tags
}

resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4o-deployment"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-08-06"
  }
  
  scale {
    type     = "Standard"
    capacity = 10
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }
  
  scale {
    type     = "Standard"
    capacity = 10
  }
}