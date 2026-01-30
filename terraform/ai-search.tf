resource "azurerm_search_service" "demo" {
  name                = "openshift-demo-search-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.demo.name
  location            = var.location
  
  sku = var.use_free_tier ? "free" : "basic"
  
  replica_count   = 1
  partition_count = 1
  
  public_network_access_enabled = true
  
  tags = azurerm_resource_group.demo.tags