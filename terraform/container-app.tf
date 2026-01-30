# Azure Container Registry
resource "azurerm_container_registry" "demo" {
  name                = "openshiftdemo${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  sku                 = "Basic"
  admin_enabled       = true
  
  tags = azurerm_resource_group.demo.tags
}

# Container Apps Environment
resource "azurerm_container_app_environment" "demo" {
  name                = "openshift-demo-env"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  
  tags = azurerm_resource_group.demo.tags
}

# Container App
resource "azurerm_container_app" "demo" {
  name                         = "openshift-rag-app"
  container_app_environment_id = azurerm_container_app_environment.demo.id
  resource_group_name          = azurerm_resource_group.demo.name
  revision_mode                = "Single"
  
  template {
    container {
      name   = "openshift-rag-demo"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"
      
      env {
        name  = "OPENAI_ENDPOINT"
        value = azurerm_cognitive_account.openai.endpoint
      }
      
      env {
        name  = "OPENAI_API_KEY"
        secret_name = "openai-key"
      }
      
      env {
        name  = "SEARCH_ENDPOINT"
        value = "https://${azurerm_search_service.demo.name}.search.windows.net"
      }
      
      env {
        name  = "SEARCH_KEY"
        secret_name = "search-key"
      }
    }
  }
  
  secret {
    name  = "openai-key"
    value = azurerm_cognitive_account.openai.primary_access_key
  }
  
  secret {
    name  = "search-key"
    value = azurerm_search_service.demo.primary_key
  }
  
  ingress {
    external_enabled = true
    target_port      = 5000
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  
  tags = azurerm_resource_group.demo.tags
}