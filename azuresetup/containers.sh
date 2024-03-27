# assume you have the az CLI tool installed.

az acr create --resource-group rg-docintel --name acrwezoimages --sku Basic --location westus3

# save the username and password from this to an Azure Key Vault.
az ad sp create-for-rbac --name http://acrwezoimages-push --scopes /subscriptions/f48a2553-c966-4d06-8faa-c5096da10254/resourceGroups/rg-docintel/providers/Microsoft.ContainerRegistry/registries/acrwezoimages --role AcrPush
