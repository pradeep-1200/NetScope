import dns.resolver

def get_resolver() -> dns.resolver.Resolver:
    """
    Returns a configured DNS resolver with public nameservers and custom timeouts.
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
    resolver.timeout = 3
    resolver.lifetime = 5
    return resolver

# Shared instance
shared_resolver = get_resolver()
