# Deploying to Azure Container Apps

## Prerequisites
- Azure CLI `az` installed and logged in (`az login`)
- Resource group for the app
- Access to an Azure Container Registry (ACR) or permissions to create one

## 1) Set environment
```bash
RESOURCE_GROUP=suno-prompter-rg
LOCATION=eastus
ACR_NAME=sunoprompteracr
IMAGE_NAME=suno-prompter
TAG=latest
```

## 2) Create resource group and ACR
```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --name $ACR_NAME --resource-group $RESOURCE_GROUP --sku Basic
az acr login --name $ACR_NAME
```

## 3) Build and push the image

Local Docker (if available):
```bash
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG
```

ACR cloud build (no local Docker needed):
```bash
az acr build --registry $ACR_NAME --image $IMAGE_NAME:$TAG .
```

## 4) Create the Container Apps environment
```bash
ACA_ENV=suno-prompter-env
az containerapp env create \
  --name $ACA_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## 5) Deploy the app
```bash
az containerapp create \
  --name suno-prompter \
  --resource-group $RESOURCE_GROUP \
  --environment $ACA_ENV \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG \
  --target-port 5000 \
  --ingress external \
  --env-vars \
    PORT=5000 \
    LLM_PROVIDER=openai \
    OPENAI_API_KEY=*** \
    OPENAI_CHAT_MODEL_ID=gpt-4o
```
Add any other LLM-specific variables you need (Azure OpenAI keys, base URL overrides, etc.).

## 6) Update to a new image
```bash
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG
az containerapp update \
  --name suno-prompter \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG
```

The container serves both the Flask API and the built React frontend on port 5000. Use `/api/generate-prompt` for API calls; all other routes serve the SPA.
