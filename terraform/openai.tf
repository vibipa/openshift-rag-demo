resource "azurerm_cognitive_account" "openai" {
  name                = "openshift-demo-openai-${random_string.suffix.result}"
  location            = var.location
  resource_group_name = azurerm_resource_group.demo.name
  kind                = "OpenAI"
  sku_name            = "S0"
  
  custom_subdomain_name = "openshift-demo-openai-${random_string.suffix.result}"
  public_network_access_enabled = true
  
  tags = azurerm_resource_group.demo.tags
}

resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4-deployment"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  
  model {
    format  = "OpenAI"
    name    = "gpt-4"
    version = "0613"
  }
  
  sku {
    name     = "Standard"
    capacity = 10
  }
}