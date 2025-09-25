# Azure Healthcare RAG Resources Summary
Generated: 2025-09-24 18:33:52

## Created Resources

### Resource Group
- Name: rg-ved-rag
- Location: eastus2
- Subscription: 8c48242c-a20e-448a-ac0f-be75ac5ebad0

### Storage Account
- Name: stvedrag
- Container: health-docs
- Tier: Standard_LRS (Hot)
- Estimated Monthly Cost: ~-5

### Azure AI Search
- Name: srch-ved-rag
- Tier: Free (Limited to 50 MB, 10,000 documents)
- Estimated Monthly Cost:  (Free tier)

### Azure OpenAI
- Name: aoai-ved-rag
- Tier: Standard (S0)
- Models Deployed:
  - text-embedding-3-small (1 unit capacity)
  - gpt-4o-mini (1 unit capacity)
- Estimated Monthly Cost: ~-20 (depends on usage)

## Access Information
All connection strings and keys have been saved to .env file.

## Next Steps
1. Verify model deployments in Azure Portal
2. Test connectivity using the generated .env file
3. Upload healthcare documents to the storage container
4. Configure your RAG application

## Cleanup
To delete all resources: az group delete --name rg-ved-rag --yes --no-wait
