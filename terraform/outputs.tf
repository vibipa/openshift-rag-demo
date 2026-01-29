output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  value     = azurerm_cognitive_account.openai.primary_access_key
  sensitive = true
}

output "gpt4_deployment_name" {
  value = azurerm_cognitive_deployment.gpt4.name
}

output "search_endpoint" {
  value = "https://${azurerm_search_service.demo.name}.search.windows.net"
}

output "search_admin_key" {
  value     = azurerm_search_service.demo.primary_key
  sensitive = true
}

output "search_service_name" {
  value = azurerm_search_service.demo.name
}