from buzzerboy_saas_tenants.saas_tenants.models.authentication import IdentityProvider

def is_subdomain(input_domain):
    # Normalize the input domain
    input_domain = input_domain.lower()

    # Fetch all root domains from the database
    root_domains = IdentityProvider.objects.values_list('domain', flat=True)

    # Check if the input domain belongs to any of the root domains
    for root_domain in root_domains:
        root_domain = root_domain.lower()
        if input_domain == root_domain or input_domain.endswith(f".{root_domain}"):
            return True

    return False
