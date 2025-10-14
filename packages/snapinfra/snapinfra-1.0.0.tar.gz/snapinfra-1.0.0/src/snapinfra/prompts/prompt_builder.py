"""Enhanced prompt building for SnapInfra infrastructure code generation."""

import re
from typing import List, Optional, Tuple

from .system_prompts import get_system_prompt


def detect_infrastructure_type(prompt: str) -> Optional[str]:
    """
    Detect infrastructure type from user prompt.
    
    Args:
        prompt: User's input prompt
        
    Returns:
        Detected infrastructure type or None
    """
    prompt_lower = prompt.lower()
    
    # Infrastructure type patterns (order matters for specificity)
    patterns = [
        (r'\b(terraform|tf)\b', 'terraform'),
        (r'\b(kubernetes|k8s|kube)\b', 'kubernetes'),
        (r'\b(docker|dockerfile|container)\b', 'docker'),
        (r'\b(docker-compose|compose)\b', 'docker'),
        (r'\b(cloudformation|cfn)\b', 'aws'),
        (r'\b(pulumi)\b', 'terraform'),  # Use terraform prompt as base
        (r'\b(ansible|playbook)\b', 'ansible'),
        (r'\b(aws|amazon|ec2|s3|lambda|rds|vpc|iam)\b', 'aws'),
        (r'\b(azure|az)\b', 'azure'), 
        (r'\b(gcp|google|gcloud)\b', 'gcp'),
        (r'\b(helm|chart)\b', 'kubernetes'),
        (r'\b(manifest|deployment|service|ingress|configmap|secret)\b', 'kubernetes'),
    ]
    
    for pattern, infra_type in patterns:
        if re.search(pattern, prompt_lower):
            return infra_type
    
    return None


def extract_key_components(prompt: str) -> List[str]:
    """
    Extract key infrastructure components from prompt.
    
    Args:
        prompt: User's input prompt
        
    Returns:
        List of detected components
    """
    prompt_lower = prompt.lower()
    components = []
    
    # Common infrastructure components
    component_patterns = {
        'load_balancer': r'\b(load.?balancer|alb|nlb|elb|lb)\b',
        'database': r'\b(database|db|rds|mysql|postgres|mongodb|redis|elasticsearch)\b',
        'storage': r'\b(storage|s3|blob|bucket|volume|pv|pvc)\b',
        'networking': r'\b(vpc|vnet|subnet|security.?group|nacl|firewall|route)\b',
        'compute': r'\b(instance|vm|ec2|compute|node|server)\b',
        'container': r'\b(container|docker|pod|deployment)\b',
        'monitoring': r'\b(monitoring|logging|cloudwatch|prometheus|grafana|alert)\b',
        'api': r'\b(api|gateway|rest|graphql|endpoint)\b',
        'queue': r'\b(queue|sqs|pubsub|kafka|messaging)\b',
        'cache': r'\b(cache|redis|memcached|elasticache)\b',
        'cdn': r'\b(cdn|cloudfront|distribution)\b',
        'identity': r'\b(iam|rbac|auth|identity|sso)\b',
    }
    
    for component, pattern in component_patterns.items():
        if re.search(pattern, prompt_lower):
            components.append(component)
    
    return components


def extract_requirements(prompt: str) -> List[str]:
    """
    Extract specific requirements from prompt.
    
    Args:
        prompt: User's input prompt
        
    Returns:
        List of detected requirements
    """
    prompt_lower = prompt.lower()
    requirements = []
    
    requirement_patterns = {
        'high_availability': r'\b(high.?availability|ha|multi.?az|failover|redundant)\b',
        'secure': r'\b(secure|security|encrypted|ssl|tls|https)\b',
        'scalable': r'\b(scalable|scaling|autoscaling|elastic)\b',
        'production': r'\b(production|prod|enterprise|commercial)\b',
        'development': r'\b(development|dev|testing|staging)\b',
        'cost_optimized': r'\b(cost.?optim|cheap|budget|low.?cost)\b',
        'managed': r'\b(managed|serverless|saas|paas)\b',
        'backup': r'\b(backup|snapshot|recovery|restore)\b',
        'monitoring': r'\b(monitor|observability|metrics|logs|alerts)\b',
    }
    
    for requirement, pattern in requirement_patterns.items():
        if re.search(pattern, prompt_lower):
            requirements.append(requirement)
    
    return requirements


def build_enhanced_prompt(
    user_prompt: str,
    include_explanations: bool = False
) -> Tuple[str, str]:
    """
    Build enhanced prompt with system message and user message.
    
    Args:
        user_prompt: User's original prompt
        include_explanations: Whether to include detailed explanations
        
    Returns:
        Tuple of (system_prompt, enhanced_user_prompt)
    """
    # Detect infrastructure type
    infra_type = detect_infrastructure_type(user_prompt)
    
    # Get appropriate system prompt
    system_prompt = get_system_prompt(infra_type)
    
    # Extract components and requirements
    components = extract_key_components(user_prompt)
    requirements = extract_requirements(user_prompt)
    
    # Build enhanced user prompt
    enhanced_prompt_parts = []
    
    # Start with original request
    enhanced_prompt_parts.append(f"Generate infrastructure code for: {user_prompt}")
    
    # Add detected components context
    if components:
        enhanced_prompt_parts.append(f"\\nKey components to include: {', '.join(components)}")
    
    # Add requirements context  
    if requirements:
        enhanced_prompt_parts.append(f"\\nRequirements: {', '.join(req.replace('_', ' ') for req in requirements)}")
    
    # Add explanation requirement
    if include_explanations:
        enhanced_prompt_parts.append("\\nInclude detailed explanations and deployment instructions.")
    
    # Add security and best practices reminder
    enhanced_prompt_parts.append("\\nEnsure the configuration follows security best practices and is production-ready.")
    
    enhanced_user_prompt = "".join(enhanced_prompt_parts)
    
    return system_prompt, enhanced_user_prompt


def improve_user_prompt(original_prompt: str) -> str:
    """
    Improve user prompt by making it more specific and actionable.
    
    Args:
        original_prompt: User's original prompt
        
    Returns:
        Improved prompt string
    """
    # Remove common prefixes that don't add value
    cleaned = original_prompt.strip()
    prefixes_to_remove = [
        "generate sample code for a",
        "generate code for a", 
        "generate sample code for",
        "generate code for",
        "create a",
        "create",
        "build a",
        "build",
        "make a",
        "make",
    ]
    
    cleaned_lower = cleaned.lower()
    for prefix in prefixes_to_remove:
        if cleaned_lower.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    
    # Ensure it starts with a capital letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    
    # Add context for better code generation
    infra_type = detect_infrastructure_type(cleaned)
    components = extract_key_components(cleaned)
    
    improvements = []
    
    # Add specific infrastructure context
    if infra_type == 'terraform':
        improvements.append("Create a complete Terraform configuration")
    elif infra_type == 'kubernetes':
        improvements.append("Create Kubernetes manifests")
    elif infra_type == 'docker':
        improvements.append("Create a Dockerfile and related configuration")
    elif infra_type in ['aws', 'azure', 'gcp']:
        improvements.append(f"Create infrastructure configuration for {infra_type.upper()}")
    
    if improvements:
        return f"{' '.join(improvements)} for {cleaned}"
    
    return f"Create infrastructure configuration for {cleaned}"