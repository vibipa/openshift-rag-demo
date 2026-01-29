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