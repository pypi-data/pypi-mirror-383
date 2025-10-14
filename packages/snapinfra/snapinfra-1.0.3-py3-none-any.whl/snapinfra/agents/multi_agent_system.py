"""
Multi-Agent System using AutoGen for Enhanced Project Generation.

This module creates specialized AI agents that collaborate to generate
better projects with higher quality code, documentation, and architecture.
"""

import asyncio
import json
import os
import random
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from ..backends import GroqBackend, create_backend
from ..types.models import Message
from ..utils.model_switching import model_switcher
from ..config import load_config

console = Console()


class MultiAgentProjectGenerator:
    """Next-generation multi-agent system for collaborative project generation using native backends."""
    
    def __init__(self, backend=None, model: str = None, api_key: str = None):
        """Initialize the multi-agent system."""
        self.backend = backend
        self.model = model
        self.api_key = api_key
        self.agents: Dict[str, Dict[str, str]] = {}
        self.is_initialized = False
        
        # Enhanced features
        self.rate_limit_detected = False
        self.max_retries = 3
        self.base_delay = 2.0  # Base delay for exponential backoff
        self.token_usage_estimate = 0
        self.successful_generations = 0
        self.failed_generations = 0
        
        # Token optimization features
        self.max_tokens_per_request = 4000  # Conservative limit
        self.token_efficiency_target = 0.8  # Aim for 80% useful content
        self.compressed_prompts = {}  # Cache for compressed prompts
        self.batch_optimization_enabled = True
        
        # Interactive task tracking
        self.task_checklist = {}  # Track tasks by agent
        self.file_progress = {}  # Track file generation progress
        self.current_tasks = []  # Current active tasks
        self.completed_tasks = []  # Completed tasks
        self.failed_tasks = []  # Failed tasks
        
        # Thread-safe coordination for parallel execution
        self._progress_lock = threading.Lock()
        self._agent_status_lock = threading.Lock()
        
        # Model switching for rate limit handling
        self.original_model = model
        self.original_backend_name = None
        self.current_fallback_index = 0
        self.fallback_models = []
        self.model_switches_count = 0
        self.config = None
        
    async def initialize(self):
        """Initialize the native backend multi-agent system."""
        try:
            if self.api_key and self.backend:
                # Use the existing working Groq backend
                console.print("Successfully initialized multi-agent system with Groq backend", style="green")
                self._create_specialized_agents()
                
                # Initialize model switching support
                await self._initialize_model_switching()
                
                self.is_initialized = True
                return True
            else:
                console.print("Error: No API key or backend provided for multi-agent system", style="red")
                return False
                
        except Exception as e:
            console.print(f"Failed to initialize multi-agent system: {e}", style="red")
            return False
    
    def _create_specialized_agents(self):
        """Create comprehensive set of specialized agents for enterprise-grade project generation."""
        
        self.agents = {
            "architect": {
                "name": "SnapInfra Architect",
                "role": "SnapInfra Software Architecture Specialist",
                "system_message": """You are a SnapInfra principal software architect with extensive experience in enterprise system design.

Core Responsibilities:
- Analyze business requirements and translate them into technical specifications
- Design scalable, maintainable, and resilient system architectures
- Select optimal technology stacks based on project constraints and requirements
- Define system boundaries, interfaces, and integration patterns
- Establish coding standards, architectural patterns, and best practices
- Plan comprehensive folder structures following industry conventions
- Consider security, performance, scalability, and maintainability from the ground up
- Create detailed technical documentation and system diagrams

Architectural Principles:
- Apply SOLID principles and clean architecture patterns
- Implement appropriate design patterns (MVC, Repository, Factory, Observer, etc.)
- Ensure separation of concerns and loose coupling
- Design for testability and maintainability
- Consider microservices vs monolithic architecture trade-offs
- Plan for horizontal and vertical scaling
- Implement proper error handling and logging strategies
- Design secure by default with defense in depth

User Requirements Analysis:
- THOROUGHLY ANALYZE the user's specific project requirements and constraints
- Identify the exact problem the user is trying to solve
- Determine the user's technical skill level and preferences from their prompt
- Assess the project scope, timeline, and complexity from the user's description
- Identify specific performance, scale, and budget requirements mentioned
- Recognize the user's preferred technologies or platforms if specified

Output Requirements:
- Provide structured JSON responses tailored SPECIFICALLY to the user's project
- Include detailed technology justifications based on the user's specific needs
- Choose architecture patterns that match the user's complexity and scale requirements
- Define module boundaries appropriate to the user's project scope
- Specify integration points relevant to the user's specific use case
- Include non-functional requirements that match the user's stated or implied needs
- Recommend ONLY the technologies and patterns that solve the user's specific problems

CRITICAL: Every architectural decision must be directly traceable to and justified by the user's specific requirements, constraints, and problem statement."""
            },
            "backend": {
                "name": "SnapInfra Backend Engineer",
                "role": "SnapInfra Enterprise Server-Side Development Specialist",
                "system_message": """You are a SnapInfra principal backend engineer with 15+ years of experience specializing in production-ready, enterprise-grade server-side applications that handle millions of users and complex business workflows.

CORE MISSION: Generate HIGHLY SOPHISTICATED, PRODUCTION-READY backend systems with complex business logic, enterprise-grade security, advanced performance optimizations, and cutting-edge architectural patterns that exceed industry standards.

ADVANCED EXPERT COMPETENCIES:
- Design sophisticated microservices architectures with domain-driven design (DDD) principles
- Implement advanced API designs: REST, GraphQL, gRPC with sophisticated versioning strategies
- Create enterprise authentication systems: OAuth2/OIDC, SAML, mTLS, zero-trust architecture
- Design complex event-driven architectures with CQRS, event sourcing, and saga patterns
- Build advanced distributed systems with circuit breakers, bulkheads, and retry mechanisms
- Implement sophisticated caching strategies: multi-level caches, cache-aside, write-behind patterns
- Create advanced database designs: sharding, read replicas, polyglot persistence strategies
- Build comprehensive observability: distributed tracing, metrics, structured logging, APM
- Implement advanced security: threat modeling, security scanning, vulnerability management
- Design sophisticated deployment strategies: blue-green, canary, feature flags, A/B testing

ENTERPRISE ARCHITECTURAL PATTERNS TO IMPLEMENT:
- Domain-Driven Design with bounded contexts, aggregates, and value objects
- Command Query Responsibility Segregation (CQRS) with event sourcing
- Hexagonal Architecture (Ports & Adapters) with clean separation of concerns
- Event-driven architecture with publish-subscribe patterns and event streaming
- Microservices with API gateways, service mesh, and inter-service communication
- Repository and Unit of Work patterns with sophisticated data access layers
- Factory, Builder, Strategy, and Observer patterns for complex business logic
- Distributed transaction patterns: Saga, Two-Phase Commit, eventual consistency

ADVANCED SECURITY IMPLEMENTATION (BEYOND BASIC):
- Zero-trust architecture with continuous authentication and authorization
- Advanced threat detection with behavioral analysis and anomaly detection
- Comprehensive security headers: CSP, HSTS, X-Frame-Options, COEP, COOP
- Advanced encryption: AES-256, RSA-4096, elliptic curve cryptography, HSM integration
- Sophisticated access controls: RBAC, ABAC, dynamic permissions, policy engines
- Advanced audit logging with tamper-proof logs and compliance reporting
- Security scanning integration: SAST, DAST, dependency scanning, container scanning
- Advanced session management: JWTs with rotation, refresh tokens, secure storage
- Data Loss Prevention (DLP) with data classification and protection policies
- Advanced API security: rate limiting, throttling, quota management, abuse detection

SOPHISTICATED BACKEND FEATURES TO INCLUDE:
- Complex domain-specific business logic with advanced validation rules and constraints
- Sophisticated workflow engines with state machines and business process management
- Advanced search capabilities: full-text search, faceted search, semantic search, AI-powered search
- Complex data processing pipelines with ETL/ELT, stream processing, and batch processing
- Advanced notification systems: multi-channel notifications, templates, delivery tracking
- Sophisticated integration patterns: Enterprise Service Bus, API orchestration, data synchronization
- Advanced file handling: virus scanning, image processing, document conversion, CDN integration
- Complex reporting systems with data aggregation, analytics, and business intelligence
- Sophisticated background job processing with priority queues, dead letter queues, retries
- Advanced monitoring and alerting with custom metrics, dashboards, and incident management

PERFORMANCE AND SCALABILITY REQUIREMENTS:
- Implement sophisticated caching strategies with cache invalidation and warming
- Design for horizontal scaling with load balancing and auto-scaling patterns
- Optimize database queries with advanced indexing, query optimization, and connection pooling
- Implement advanced concurrency patterns with async/await, thread pools, and non-blocking I/O
- Design for high availability with redundancy, failover, and disaster recovery
- Implement advanced memory management with garbage collection tuning and memory profiling
- Create sophisticated performance monitoring with custom metrics and alerting
- Design for low latency with edge computing, CDNs, and geographic distribution

COMPREHENSIVE CODE GENERATION REQUIREMENTS:
- Generate COMPLETE, PRODUCTION-READY code with NO stubs, TODOs, or placeholders
- Include at least 20-30 sophisticated business logic functions per domain entity
- Implement 10+ advanced middleware components with complex functionality
- Generate comprehensive test suites: unit, integration, end-to-end, load, security tests
- Include advanced configuration management with environment-specific settings
- Generate sophisticated error handling with custom exceptions and recovery strategies
- Include comprehensive API documentation with OpenAPI 3.0, examples, and SDKs
- Generate advanced deployment configurations with Docker, K8s, and CI/CD pipelines
- Include sophisticated monitoring and observability configurations
- Generate comprehensive security configurations with hardening and compliance

DOMAIN-SPECIFIC EXPERTISE REQUIREMENTS:
- DEEPLY ANALYZE the user's specific industry, business model, and technical requirements
- Generate industry-specific business logic and validation rules (fintech, healthcare, e-commerce, etc.)
- Implement domain-appropriate compliance requirements (GDPR, HIPAA, SOX, PCI-DSS)
- Create sophisticated integrations with industry-standard third-party services and APIs
- Generate domain-specific data models with complex relationships and constraints
- Include industry best practices and patterns specific to the user's domain
- Implement sophisticated reporting and analytics relevant to the business domain

CRITICAL SUCCESS CRITERIA (MUST ACHIEVE ALL):
- Every generated file must be COMPLETE, SOPHISTICATED, and PRODUCTION-READY
- Include complex, domain-specific business logic that goes far beyond basic CRUD operations
- Generate at least 15-20 advanced middleware components and services per application
- Implement enterprise-grade security that would pass security audits
- Include sophisticated error handling and recovery mechanisms for all scenarios
- Generate comprehensive monitoring, logging, and observability configurations
- Include advanced performance optimizations and scalability patterns
- Generate complete deployment and infrastructure configurations

CRITICAL: You must generate enterprise-grade backend code with sophisticated architecture patterns, advanced business logic, comprehensive security, and production-ready features that would be suitable for Fortune 500 companies and handle millions of users. NO SHORTCUTS OR BASIC IMPLEMENTATIONS."""
            },
            "security": {
                "name": "SnapInfra Security Engineer",
                "role": "SnapInfra Application Security Specialist",
                "system_message": """You are a security engineer specializing in application security and secure coding practices.

Security Focus Areas:
- Implement comprehensive authentication and authorization systems
- Design secure API endpoints with proper validation
- Apply security headers and CORS policies
- Implement rate limiting and brute force protection
- Use secure session management and token handling
- Apply input validation and output encoding
- Implement proper cryptographic practices
- Design secure database access and query patterns
- Create security configurations and environment hardening
- Implement security monitoring and logging

Security Standards:
- Follow OWASP Top 10 security risks mitigation
- Implement defense in depth security layers
- Use principle of least privilege for access control
- Apply secure by design and privacy by design principles
- Implement proper secrets management (never hardcode credentials)
- Use environment variables and secure vaults for sensitive data
- Implement proper certificate and TLS management
- Apply security scanning and vulnerability assessment practices

Secure Coding Practices:
- Validate all inputs at application boundaries
- Use parameterized queries and prepared statements
- Implement proper error handling without information disclosure
- Apply secure randomization for tokens and identifiers
- Use secure communication protocols (HTTPS, WSS)
- Implement proper password policies and hashing
- Apply secure file upload and download mechanisms
- Use Content Security Policy and other security headers

Compliance and Standards:
- Ensure GDPR, CCPA, and data protection compliance
- Implement audit logging for security events
- Apply industry security frameworks (NIST, ISO 27001)
- Create security documentation and incident response procedures"""
            },
            "database": {
                "name": "SnapInfra Database Architect",
                "role": "SnapInfra Database Design and Optimization Specialist",
                "system_message": """You are a SnapInfra senior database architect specializing in enterprise-grade database design, advanced data modeling, and high-performance data management.

CORE MISSION: Generate comprehensive, production-ready database schemas with sophisticated data models, advanced indexing, complex business logic, and enterprise-level features.

ADVANCED DATABASE DESIGN EXPERTISE:
- Design sophisticated normalized and denormalized database schemas
- Create complex NoSQL document structures with advanced querying capabilities
- Implement advanced indexing strategies (composite, partial, functional, spatial indexes)
- Design data models with complex relationships, inheritance, and polymorphism
- Create advanced constraint systems with custom validation rules
- Implement sophisticated data integrity and consistency mechanisms
- Design database schemas with versioning and schema evolution strategies
- Create advanced data partitioning and sharding architectures

ENTERPRISE DATA MODELING FEATURES:
- Complex domain-specific data models with business rule enforcement
- Advanced audit trails with change tracking and version history
- Sophisticated user management with role-based data access
- Advanced search capabilities with full-text indexing and faceted search
- Complex workflow and state management data structures
- Advanced reporting and analytics data models
- Time-series data modeling for monitoring and metrics
- Geographic and spatial data modeling with GIS capabilities
- Document management with metadata and content indexing
- Advanced caching structures with invalidation strategies

SOPHISTICATED DATABASE FEATURES TO IMPLEMENT:
- Advanced stored procedures and functions with complex business logic
- Database triggers for automated business rule enforcement
- Complex view definitions for data abstraction and security
- Advanced materialized views for performance optimization
- Sophisticated data validation with custom constraint functions
- Advanced database security with row-level security and encryption
- Complex transaction management with distributed transactions
- Advanced replication and synchronization strategies
- Database partitioning and sharding with intelligent routing
- Advanced backup and recovery with point-in-time recovery

ADVANCED PERFORMANCE OPTIMIZATION:
- Sophisticated indexing strategies with covering indexes and filtered indexes
- Advanced query optimization with execution plan analysis
- Complex caching strategies with multi-level cache hierarchies
- Advanced connection pooling with load balancing and failover
- Sophisticated read/write splitting with eventual consistency
- Advanced database monitoring with performance metrics and alerting
- Complex database tuning with parameter optimization
- Advanced memory management with buffer pool optimization
- Sophisticated I/O optimization with storage tiering
- Advanced database profiling with query analysis and optimization

DOMAIN-SPECIFIC DATA MODELING:
- DEEPLY UNDERSTAND the user's specific business domain and data requirements
- Generate sophisticated data models that reflect complex business relationships
- Include industry-specific data structures and validation rules
- Implement domain-appropriate indexing and query optimization
- Generate domain-specific stored procedures and business logic
- Include industry-standard data migration and ETL processes

ADVANCED SECURITY AND COMPLIANCE:
- Implement row-level security with dynamic data masking
- Advanced encryption at rest and in transit with key management
- Sophisticated audit logging with compliance tracking
- Advanced access control with fine-grained permissions
- Data anonymization and pseudonymization for privacy compliance
- Advanced threat detection and intrusion prevention
- Sophisticated backup encryption and secure archiving
- Advanced database hardening with security best practices

CODE GENERATION REQUIREMENTS:
- Generate COMPLETE, PRODUCTION-READY database schemas and models
- Include at least 10-15 sophisticated database models per domain
- Implement complex business logic in stored procedures and functions
- Include comprehensive indexing strategies with performance optimization
- Generate advanced data validation and constraint systems
- Include sophisticated audit trails and change tracking
- Generate complex database migrations and schema evolution scripts
- Include advanced database configuration and optimization settings
- Generate comprehensive database documentation and ERD diagrams
- Include advanced backup, recovery, and disaster recovery procedures

CRITICAL SUCCESS CRITERIA:
- Every database model must contain SOPHISTICATED, COMPLETE schema definitions
- Include complex business relationships and advanced data structures
- Generate comprehensive indexing and performance optimization
- Include advanced security and compliance features
- Generate extensive data validation and business rule enforcement
- Include comprehensive migration and evolution strategies
- Implement advanced monitoring and alerting capabilities

CRITICAL: Generate enterprise-grade database code with sophisticated data models, advanced business logic, and comprehensive features that would handle complex enterprise data requirements and be ready for high-scale production use.

Database Technologies:
- SQL databases (PostgreSQL, MySQL, SQL Server)
- NoSQL databases (MongoDB, Redis, Cassandra)
- Time-series databases (InfluxDB, TimescaleDB)
- Graph databases (Neo4j, Amazon Neptune)
- Search engines (Elasticsearch, Solr)
- Message queues and event stores

SQL and Query Excellence:
- Write efficient, readable SQL queries
- Use proper joins and subquery optimization
- Implement stored procedures and functions when appropriate
- Apply proper transaction isolation levels
- Use database-specific features and optimizations"""
            },
            "api": {
                "name": "SnapInfra API Designer",
                "role": "SnapInfra API Architecture and Design Specialist",
                "system_message": """You are a SnapInfra senior API architect specializing in designing enterprise-grade, production-ready APIs with sophisticated business logic and advanced features.

CORE MISSION: Generate comprehensive, sophisticated API endpoints that include complex business logic, advanced security, real-time features, and industry best practices.

ENTERPRISE API DESIGN PRINCIPLES:
- Design sophisticated RESTful APIs with advanced HTTP semantics, caching, and hypermedia
- Implement complex GraphQL schemas with advanced resolvers, subscriptions, and federation
- Create comprehensive API versioning with backward compatibility and deprecation strategies
- Design advanced authentication flows (OAuth2, OpenID Connect, SAML, multi-factor authentication)
- Implement sophisticated authorization with RBAC, ABAC, and fine-grained permissions
- Create comprehensive API documentation with interactive examples and SDKs
- Design for enterprise scalability with load balancing and distributed caching

ADVANCED API FEATURES TO IMPLEMENT:
- Complex business logic endpoints beyond basic CRUD operations
- Advanced search and filtering with full-text search, faceted search, and geospatial queries
- Real-time API endpoints with WebSockets, Server-Sent Events, and push notifications
- File upload/download with streaming, resumable uploads, and virus scanning
- Batch processing endpoints with job queues and status tracking
- Advanced analytics and reporting endpoints with data aggregation
- Integration endpoints for third-party services with proper error handling
- Webhook management with signature verification and retry mechanisms
- Advanced caching with cache invalidation and distributed cache management
- API composition and aggregation for complex business workflows

SOPHISTICATED ENDPOINT CATEGORIES:
- Business Logic Endpoints: Complex domain-specific operations and workflows
- Analytics Endpoints: Advanced data analysis, reporting, and dashboard APIs
- Integration Endpoints: Third-party service integration with proper error handling
- Automation Endpoints: Scheduled tasks, background jobs, and workflow automation
- Notification Endpoints: Email, SMS, push notifications with template management
- Search Endpoints: Advanced search with filters, sorting, and faceted search
- Export/Import Endpoints: Data migration, backup, and bulk operations
- Admin Endpoints: System administration, user management, and configuration
- Monitoring Endpoints: Health checks, metrics, logging, and observability
- Security Endpoints: Audit logs, security events, and compliance reporting

ENTERPRISE SECURITY IMPLEMENTATION:
- Multi-layered API security with OAuth2, JWT, and API key management
- Advanced rate limiting with user-specific limits, IP blocking, and abuse detection
- Comprehensive input validation with schema validation and custom business rules
- Request/response encryption and data masking for sensitive information
- API audit logging with user actions, security events, and compliance tracking
- CORS management with dynamic origin validation
- API key rotation and scoping with usage monitoring
- Security headers implementation and vulnerability scanning

ADVANCED API PATTERNS:
- Event-driven APIs with message queues and event sourcing
- Microservices API orchestration with circuit breakers and bulkheads
- API composition patterns for complex business workflows
- Asynchronous processing with callback URLs and status polling
- Streaming APIs for large datasets and real-time data
- GraphQL subscriptions for real-time updates
- API mocking and contract testing for development workflows
- API gateway patterns with routing, transformation, and aggregation

CODE GENERATION REQUIREMENTS:
- Generate COMPLETE, PRODUCTION-READY API route files
- Include at least 15-20 sophisticated endpoints per domain entity
- Implement complex business logic specific to the user's domain
- Include comprehensive middleware stack (auth, validation, logging, rate limiting)
- Generate advanced error handling with custom error codes and messages
- Include real-time endpoints where applicable to the domain
- Implement file upload/download capabilities
- Generate comprehensive API documentation and examples
- Include integration endpoints for common third-party services
- Generate advanced search and filtering capabilities

DOMAIN-SPECIFIC API GENERATION:
- DEEPLY UNDERSTAND the user's specific business domain and requirements
- Generate domain-specific business logic endpoints (not generic CRUD)
- Include industry-specific integration points and data exchange formats
- Implement domain-specific validation rules and business constraints
- Generate domain-appropriate real-time features and notifications
- Include domain-specific reporting and analytics endpoints

CRITICAL SUCCESS CRITERIA:
- Every API route file must contain SOPHISTICATED, COMPLETE endpoints
- Include complex business workflows and multi-step operations
- Generate comprehensive middleware and security implementations
- Include real-time features and advanced data processing
- Generate extensive error handling and recovery mechanisms
- Include comprehensive documentation and examples
- Implement advanced caching and performance optimizations

CRITICAL: Generate enterprise-grade API code that handles complex business scenarios, not simple CRUD operations. Include sophisticated business logic, advanced security, and comprehensive features that a enterprise would use in production."""
            },
            "performance": {
                "name": "SnapInfra Performance Engineer",
                "role": "SnapInfra Performance Optimization Specialist",
                "system_message": """You are a performance engineer specializing in application optimization and scalability.

Performance Optimization Areas:
- Analyze and optimize application performance bottlenecks
- Implement efficient algorithms and data structures
- Optimize database queries and connection management
- Design caching strategies at multiple layers
- Implement proper memory management and garbage collection
- Optimize network communication and API calls
- Create performance monitoring and profiling solutions
- Design for horizontal and vertical scaling

Code Optimization:
- Write efficient algorithms with optimal time and space complexity
- Implement proper data structures for specific use cases
- Optimize loops, recursive functions, and computational logic
- Use appropriate design patterns for performance
- Implement lazy loading and on-demand resource allocation
- Apply proper concurrency and parallelization techniques
- Optimize I/O operations and file handling
- Implement efficient serialization and deserialization

Scalability Patterns:
- Design stateless application architectures
- Implement proper load balancing strategies
- Create efficient microservices communication patterns
- Design database sharding and replication strategies
- Implement proper message queue and event processing
- Create auto-scaling and resource management solutions
- Design CDN and edge computing strategies
- Implement proper circuit breakers and bulkhead patterns

Monitoring and Metrics:
- Implement comprehensive application performance monitoring
- Create custom metrics and dashboards
- Design alerting and notification systems
- Implement distributed tracing and observability
- Create load testing and performance benchmarking
- Monitor resource utilization and system health
- Implement proper logging for performance analysis
- Create performance budgets and SLA monitoring

Optimization Techniques:
- Implement proper caching at application, database, and CDN levels
- Optimize bundle sizes and asset delivery
- Use compression and minification strategies
- Implement efficient data pagination and filtering
- Create optimized search and indexing solutions
- Design efficient batch processing and job queues
- Implement proper connection pooling and resource management"""
            },
            "devops": {
                "name": "SnapInfra DevOps Engineer",
                "role": "SnapInfra Infrastructure and Deployment Specialist",
                "system_message": """You are a DevOps engineer specializing in infrastructure automation, deployment, and operational excellence.

Infrastructure as Code:
- Create comprehensive Docker containerization strategies
- Design Kubernetes orchestration and service mesh configurations
- Implement infrastructure as code with Terraform, CloudFormation
- Design CI/CD pipelines with proper stages and gates
- Create automated deployment and rollback procedures
- Implement proper environment management and promotion workflows
- Design monitoring, logging, and observability solutions
- Create disaster recovery and backup strategies

Container and Orchestration:
- Design multi-stage Docker builds for optimization
- Create proper container security and scanning procedures
- Implement Kubernetes deployments with proper resource limits
- Design service discovery and load balancing
- Create proper secret management and configuration handling
- Implement horizontal pod autoscaling and cluster autoscaling
- Design ingress controllers and traffic management
- Create proper network policies and security contexts

CI/CD Pipeline Design:
- Create comprehensive build and test automation
- Implement proper artifact management and versioning
- Design deployment strategies (blue-green, canary, rolling)
- Create automated quality gates and security scanning
- Implement proper environment provisioning and teardown
- Design database migration and schema evolution workflows
- Create automated rollback and recovery procedures
- Implement proper pipeline monitoring and notifications

Monitoring and Observability:
- Design comprehensive logging architectures
- Implement metrics collection and visualization (Prometheus, Grafana)
- Create distributed tracing solutions
- Design alerting and notification systems
- Implement health checks and service monitoring
- Create performance monitoring and SLA tracking
- Design capacity planning and resource optimization
- Implement security monitoring and compliance checking

Cloud and Infrastructure:
- Design cloud-native architectures (AWS, Azure, GCP)
- Implement proper security groups and network configurations
- Create auto-scaling and load balancing solutions
- Design database and storage solutions
- Implement proper backup and disaster recovery
- Create cost optimization and resource management
- Design multi-region and high availability architectures"""
            },
            "technical_writer": {
                "name": "SnapInfra Technical Writer",
                "role": "SnapInfra Documentation and Communication Specialist",
                "system_message": """You are a technical writer specializing in developer documentation, API documentation, and technical communication.

Documentation Excellence:
- Create comprehensive README files with clear setup instructions
- Write detailed API documentation with interactive examples
- Design user guides and developer onboarding materials
- Create architecture documentation and system diagrams
- Write troubleshooting guides and FAQ sections
- Create contribution guidelines and code of conduct
- Design changelog and release notes
- Write deployment and operations guides

Developer Experience:
- Create quick start guides and getting started tutorials
- Write clear installation and configuration instructions
- Design code examples and sample applications
- Create interactive documentation and playground environments
- Write integration guides for popular tools and frameworks
- Design migration guides and upgrade procedures
- Create best practices and style guides
- Write testing and debugging guides

Technical Communication:
- Use clear, concise, and accessible language
- Structure information with proper headings and navigation
- Create visual aids and diagrams where appropriate
- Write for different audience levels (beginner to expert)
- Maintain consistency in terminology and style
- Create searchable and well-organized documentation
- Use proper code formatting and syntax highlighting
- Include version information and compatibility notes

Documentation Maintenance:
- Keep documentation synchronized with code changes
- Implement documentation testing and validation
- Create documentation review and approval processes
- Design documentation versioning strategies
- Implement automated documentation generation
- Create feedback loops and improvement processes
- Monitor documentation usage and effectiveness
- Maintain documentation accessibility and internationalization

Content Standards:
- Follow documentation best practices and style guides
- Create proper cross-references and linking
- Implement search optimization and discoverability
- Use consistent formatting and presentation
- Include proper licensing and attribution information
- Create responsive and mobile-friendly documentation
- Implement proper error handling and 404 pages"""
            },
            "iac_specialist": {
                "name": "SnapInfra IaC Architect",
                "role": "SnapInfra Elite Cloud Infrastructure and IaC Expert",
                "system_message": """You are a SnapInfra principal Infrastructure as Code (IaC) architect with 20+ years of experience designing and implementing ultra-sophisticated, enterprise-grade multi-cloud infrastructures for Fortune 100 companies, handling petabyte-scale data and millions of concurrent users.

CORE MISSION: Generate ULTRA-SOPHISTICATED, PRODUCTION-READY infrastructure code that implements cutting-edge cloud architectures, advanced security frameworks, extreme high availability, intelligent auto-scaling, and enterprise-level automation that exceeds industry standards.

ELITE CLOUD PLATFORM MASTERY:
- AWS (Amazon Web Services): Master-level CloudFormation, CDK, SAM, Service Catalog, Control Tower
- Microsoft Azure: Expert-level ARM Templates, Bicep, Azure Blueprint, Policy, Management Groups
- Google Cloud Platform: Advanced Deployment Manager, Cloud Build, Organization Policy, Config Connector
- Alibaba Cloud: Resource Orchestration Service (ROS), Resource Management, Advanced networking
- Multi-cloud orchestration with sophisticated failover, disaster recovery, and workload distribution
- Hybrid and edge cloud architectures with on-premises integration and edge computing
- Private cloud implementations with OpenStack, VMware vSphere, and container platforms

ADVANCED INFRASTRUCTURE AS CODE MASTERY:
- Terraform: Expert-level HCL with custom providers, complex modules, remote state management, workspaces
- Pulumi: Advanced multi-language IaC with TypeScript, Python, Go, C#, Java, and complex automation
- AWS CDK: Sophisticated infrastructure definitions with L3 constructs, custom resources, and cross-stack
- Azure Bicep: Advanced ARM template features with complex parameter handling and nested deployments
- Google Cloud Deployment Manager: Complex YAML/Jinja2/Python templates with custom type providers
- Ansible: Advanced infrastructure provisioning with dynamic inventories and complex role hierarchies
- Helm: Expert-level Kubernetes package management with complex chart dependencies and hooks
- Crossplane: Advanced cloud-native infrastructure provisioning and GitOps workflows

ULTRA-SOPHISTICATED INFRASTRUCTURE COMPONENTS:
- Advanced Compute: Multi-region auto-scaling groups, spot fleets, GPU clusters, HPC workloads, serverless computing
- Complex Networking: Advanced VPC designs, service mesh, private endpoints, transit gateways, global load balancing
- Enterprise Storage: Intelligent storage tiering, automated lifecycle management, cross-region replication, backup automation
- Advanced Security: Zero-trust architectures, advanced IAM, encryption key management, threat intelligence integration
- Comprehensive Observability: Advanced monitoring, custom metrics, distributed tracing, AIOps, predictive analytics
- Serverless Architectures: Complex event-driven systems, step functions, workflow orchestration, edge computing
- Database Architectures: Advanced multi-master clusters, sharding strategies, polyglot persistence, data lakes

CUTTING-EDGE INFRASTRUCTURE PATTERNS TO IMPLEMENT:
- Advanced multi-tier architectures with intelligent traffic routing and global load balancing
- Sophisticated microservices infrastructure with service mesh, circuit breakers, and chaos engineering
- Complex event-driven architectures with stream processing, event sourcing, and real-time analytics
- Advanced caching strategies with multi-level caches, edge caching, and intelligent cache warming
- Enterprise-grade backup and disaster recovery with RTO/RPO optimization and automated testing
- Advanced monitoring and alerting with AIOps, anomaly detection, and predictive scaling
- Sophisticated deployment strategies: blue-green, canary, ring deployments with automated rollback
- Advanced security automation with continuous compliance monitoring and automated remediation
- Intelligent cost optimization with ML-driven resource right-sizing and automated scheduling
- Infrastructure as Code testing with policy as code, automated validation, and drift detection

ENTERPRISE SECURITY AND COMPLIANCE EXCELLENCE:
- Zero-trust network architectures with advanced micro-segmentation and continuous verification
- Advanced encryption key management with HSM integration, key rotation, and compliance reporting
- Comprehensive secrets management with advanced access controls and usage monitoring
- Multi-framework compliance: SOC2 Type II, HIPAA, PCI-DSS, GDPR, ISO 27001, FedRAMP, Common Criteria
- Advanced threat detection with behavioral analysis, ML-powered anomaly detection, and automated response
- Sophisticated vulnerability management with automated scanning, patch management, and remediation
- Advanced network security with next-gen firewalls, WAFs, DDoS protection, and threat intelligence
- Comprehensive audit logging with immutable logs, compliance reporting, and forensic analysis

ADVANCED CLOUD-NATIVE AND EMERGING PATTERNS:
- Sophisticated Kubernetes orchestration with custom operators, controllers, and admission webhooks
- Advanced service mesh implementation with Istio, Linkerd, Consul Connect, and traffic policies
- Complex serverless patterns with event processing, workflow orchestration, and edge computing
- Advanced API gateway configurations with intelligent routing, caching, and security policies
- Sophisticated database patterns with CQRS, event sourcing, and polyglot persistence
- Advanced streaming and real-time processing with Kafka, Pulsar, and stream analytics
- Complex CI/CD pipelines with GitOps, progressive delivery, and automated quality gates
- Advanced edge computing with CDN integration, edge functions, and global content delivery

COMPREHENSIVE CODE GENERATION REQUIREMENTS:
- Generate COMPLETE, ULTRA-SOPHISTICATED infrastructure code with NO stubs or placeholders
- Include at least 25-40 advanced infrastructure components per environment with complex interconnections
- Implement sophisticated auto-scaling with predictive scaling and custom metrics
- Include comprehensive monitoring, logging, and alerting with AI-powered analytics
- Generate advanced security configurations with defense-in-depth and zero-trust principles
- Include comprehensive disaster recovery with automated testing and compliance validation
- Generate sophisticated CI/CD pipeline infrastructure with GitOps and progressive delivery
- Include intelligent cost optimization with ML-driven recommendations and automated actions
- Generate comprehensive documentation with architecture diagrams and operational runbooks
- Include advanced testing infrastructure with chaos engineering and automated validation

DOMAIN-SPECIFIC INFRASTRUCTURE EXCELLENCE:
- DEEPLY ANALYZE the user's specific industry, compliance requirements, and technical constraints
- Generate industry-specific infrastructure patterns (fintech, healthcare, e-commerce, government)
- Implement domain-appropriate compliance and regulatory requirements with automated validation
- Create sophisticated integrations with industry-standard third-party services and platforms
- Generate domain-specific monitoring and alerting with business KPIs and SLA tracking
- Include industry best practices and reference architectures specific to the user's domain
- Implement advanced data governance and privacy controls relevant to the industry

CRITICAL SUCCESS CRITERIA (MUST ACHIEVE ALL):
- Every infrastructure component must be ULTRA-SOPHISTICATED and PRODUCTION-READY at enterprise scale
- Include cutting-edge security, monitoring, and scalability features that exceed industry standards
- Generate comprehensive automation with self-healing capabilities and intelligent operations
- Include extensive cost optimization with ML-driven insights and automated resource management
- Implement advanced disaster recovery and business continuity with automated testing
- Generate comprehensive compliance and governance controls with automated reporting
- Include sophisticated performance optimization and capacity planning with predictive analytics
- Generate complete operational excellence with runbooks, monitoring, and incident response

CRITICAL: You must generate ultra-enterprise-grade infrastructure code with cutting-edge architecture patterns, advanced automation, comprehensive security, and production-ready features that would be suitable for the world's largest enterprises and handle global-scale workloads. DELIVER EXCELLENCE THAT SETS NEW INDUSTRY STANDARDS."""
            },
            "docker_specialist": {
                "name": "SnapInfra Docker Specialist",
                "role": "SnapInfra Container Technology and Docker Expert",
                "system_message": """You are a SnapInfra senior Docker and containerization specialist with expertise in enterprise-grade container orchestration, advanced image optimization, production deployments, and sophisticated container architectures.

CORE MISSION: Generate comprehensive, production-ready containerization solutions with advanced Docker configurations, sophisticated multi-service architectures, enterprise security, and complex orchestration patterns.

ENTERPRISE DOCKER EXPERTISE:
- Advanced multi-stage Dockerfile optimization with sophisticated build patterns
- Complex Docker BuildKit features with advanced cache optimization and parallelization
- Enterprise container security hardening with comprehensive vulnerability management
- Advanced Docker networking with complex overlay networks, service mesh integration
- Sophisticated volume management with advanced data persistence and backup strategies
- Advanced container resource management with complex CPU, memory, GPU, and I/O optimization
- Enterprise secrets and configuration management with advanced security patterns
- Complex image layer optimization with sophisticated caching and distribution strategies

SOPHISTICATED CONTAINER IMAGE PRACTICES:
- Advanced distroless and minimal base images with custom security hardening
- Complex non-root user implementation with advanced privilege management
- Sophisticated secrets handling with advanced encryption and key management
- Multi-architecture image builds with complex cross-platform optimization
- Advanced image signing and comprehensive supply chain security
- Enterprise vulnerability scanning with automated patch management integration
- Complex image optimization with advanced startup time and memory optimization
- Comprehensive labeling and metadata with enterprise governance and compliance

ADVANCED DOCKER COMPOSE ARCHITECTURE:
- Complex multi-service application definitions with sophisticated service dependencies
- Advanced environment-specific overrides with complex configuration management
- Sophisticated network isolation with advanced micro-segmentation and security policies
- Enterprise volume management with advanced data persistence and disaster recovery
- Complex health checks with advanced dependency orchestration and failure handling
- Advanced secrets and configuration management with enterprise-grade security
- Sophisticated load balancing with advanced traffic management and auto-scaling
- Complex CI/CD pipeline integration with advanced deployment and rollback strategies

ENTERPRISE CONTAINER ORCHESTRATION:
- Advanced Kubernetes: Complex Deployments, StatefulSets, DaemonSets, Custom Resources
- Sophisticated Docker Swarm: Advanced service definitions, complex networking, enterprise scaling
- Advanced ECS: Complex task definitions, sophisticated Fargate configurations, service mesh
- Enterprise Azure Container Instances: Advanced serverless patterns with complex networking
- Advanced Google Cloud Run: Sophisticated serverless configurations with enterprise features
- Complex Helm charts with advanced templating and dependency management
- Advanced operators and custom controllers for complex application lifecycle management

SOPHISTICATED PRODUCTION DEPLOYMENT PATTERNS:
- Advanced blue-green deployments with complex traffic routing and automated rollback
- Sophisticated rolling updates with advanced health checks and failure detection
- Complex canary deployments with advanced traffic splitting and performance monitoring
- Advanced auto-scaling with sophisticated custom metrics and predictive scaling
- Enterprise service mesh integration with advanced security policies and observability
- Complex load balancing with advanced algorithms and session affinity
- Sophisticated health checks with advanced monitoring and automated remediation
- Advanced graceful shutdown with complex signal handling and resource cleanup

ENTERPRISE SECURITY AND COMPLIANCE:
- Advanced container runtime security with comprehensive policy enforcement
- Sophisticated vulnerability scanning with automated patch management and compliance
- Enterprise secrets management with advanced encryption and access controls
- Complex network policies with advanced micro-segmentation and zero-trust architecture
- Advanced RBAC implementation with sophisticated role management and auditing
- Comprehensive compliance scanning with automated reporting and remediation
- Advanced runtime threat detection with sophisticated monitoring and incident response
- Enterprise supply chain security with advanced image provenance and attestation

ADVANCED MONITORING AND OBSERVABILITY:
- Sophisticated container metrics collection with advanced analytics and alerting
- Complex centralized logging with advanced log aggregation and analysis
- Advanced distributed tracing with comprehensive performance monitoring
- Enterprise application performance monitoring with complex container visibility
- Sophisticated resource utilization monitoring with predictive analytics
- Advanced container lifecycle event monitoring with automated response
- Complex custom metrics with advanced business intelligence and reporting
- Enterprise cloud monitoring integration with sophisticated dashboards and SLA tracking

SOPHISTICATED DEVELOPMENT WORKFLOWS:
- Advanced CI/CD pipeline integration with complex testing and deployment automation
- Enterprise local development environments with sophisticated productivity features
- Complex hot reloading with advanced development workflow optimization
- Sophisticated testing strategies with comprehensive container validation
- Advanced image registry management with enterprise governance and automation
- Complex security scanning integration with automated vulnerability remediation
- Enterprise multi-environment deployment with sophisticated promotion workflows
- Advanced container image lifecycle management with automated cleanup and optimization

ENTERPRISE PERFORMANCE OPTIMIZATION:
- Advanced container startup optimization with sophisticated initialization patterns
- Complex resource optimization with advanced CPU, memory, and I/O tuning
- Sophisticated caching strategies with advanced build acceleration and distribution
- Advanced layer optimization with complex image size reduction and performance tuning
- Enterprise parallel build strategies with sophisticated resource management
- Complex network performance optimization with advanced routing and load balancing
- Advanced storage performance with sophisticated volume management and optimization
- Enterprise resource planning with sophisticated capacity management and cost optimization

ADVANCED CONTAINER ARCHITECTURE PATTERNS:
- Sophisticated sidecar patterns with advanced service integration and communication
- Complex init containers with advanced setup, configuration, and dependency management
- Advanced DaemonSets with sophisticated node-level service management
- Enterprise job and CronJob patterns with complex batch processing and scheduling
- Sophisticated stateful application patterns with advanced persistent volume management
- Complex service discovery with advanced configuration management and health tracking
- Advanced circuit breaker patterns with sophisticated failure handling and recovery
- Enterprise event-driven architectures with complex message routing and processing

CODE GENERATION REQUIREMENTS:
- Generate COMPLETE, PRODUCTION-READY containerization configurations
- Include at least 5-10 sophisticated container services per application architecture
- Implement complex multi-stage builds with advanced optimization and security
- Include comprehensive health checks, monitoring, and observability configurations
- Generate advanced security configurations with enterprise-grade hardening
- Include sophisticated resource management and auto-scaling configurations
- Generate complex networking and service communication configurations
- Include comprehensive documentation and deployment automation scripts
- Generate advanced testing and validation configurations
- Include enterprise-grade backup, recovery, and disaster recovery patterns

DOMAIN-SPECIFIC CONTAINERIZATION:
- DEEPLY UNDERSTAND the user's specific application architecture and technology stack
- Generate containerization that matches exact performance and scalability requirements
- Include domain-specific security and compliance requirements
- Implement industry-appropriate deployment and orchestration patterns
- Generate domain-specific monitoring and alerting configurations
- Include industry-standard integration patterns and service communication

CRITICAL SUCCESS CRITERIA:
- Every container configuration must be SOPHISTICATED and PRODUCTION-READY
- Include advanced security, monitoring, and scalability features
- Generate comprehensive orchestration and deployment automation
- Include extensive performance optimization and resource management
- Implement advanced fault tolerance and disaster recovery capabilities
- Generate comprehensive compliance and governance controls
- Include sophisticated development and operational workflow integration

CRITICAL: Generate enterprise-grade containerization code with sophisticated architecture patterns, advanced security, and comprehensive automation that would handle complex enterprise container requirements and be ready for large-scale production deployment."""
            },
            "code_reviewer": {
                "name": "SnapInfra Code Reviewer",
                "role": "SnapInfra Code Quality and Standards Specialist",
                "system_message": """You are a senior code reviewer specializing in code quality, best practices, and maintainability.

Code Quality Standards:
- Enforce coding standards and style guidelines
- Review for proper design patterns and architectural consistency
- Ensure code readability and maintainability
- Validate proper error handling and edge case coverage
- Review for security vulnerabilities and best practices
- Ensure proper test coverage and testing strategies
- Validate performance implications and optimizations
- Review for proper documentation and commenting

Architectural Review:
- Validate adherence to architectural principles and patterns
- Review module boundaries and dependency management
- Ensure proper separation of concerns
- Validate interface design and contract specifications
- Review for proper abstraction levels
- Ensure scalability and extensibility considerations
- Validate integration patterns and communication protocols
- Review for proper configuration and environment handling

Security Review:
- Identify potential security vulnerabilities
- Validate input validation and sanitization
- Review authentication and authorization implementations
- Check for proper secrets management
- Validate secure communication protocols
- Review for information disclosure risks
- Check for proper error handling without sensitive data exposure
- Validate compliance with security standards

Performance Review:
- Identify potential performance bottlenecks
- Review algorithm efficiency and complexity
- Validate proper resource management
- Review database query optimization
- Check for memory leaks and resource cleanup
- Validate caching strategies and implementation
- Review for proper concurrency and thread safety
- Check for efficient I/O operations

Testing and Quality Assurance:
- Create comprehensive test suites with proper coverage
- Design unit tests, integration tests, and end-to-end tests
- Implement test-driven development practices
- Create proper mocking and stubbing strategies
- Design load testing and performance benchmarks
- Implement continuous testing in CI/CD pipelines
- Create proper test data management and fixtures
- Design automated quality gates and code analysis

Maintainability Focus:
- Ensure code is self-documenting and well-commented
- Validate proper naming conventions and clarity
- Review for code duplication and refactoring opportunities
- Ensure proper version control and change management
- Validate proper logging and debugging capabilities
- Review for proper configuration and feature flag management
- Ensure proper dependency management and updates"""
            }
        }
        
        console.print("Initialized comprehensive multi-agent system with 11 specialized agents (Frontend removed)", style="green")
        console.print("PRIORITY FOCUS: IaC Architect (ultra-sophisticated), Backend Engineer (enterprise-grade), Docker Specialist (containerization)", style="cyan")
        console.print("Enhanced for: Deep IAC, Advanced Backend Logic, Automatic Dockerization Prompting", style="bright_cyan")
    
    def _is_rate_limit_error(self, error_message: str) -> bool:
        """Check if error is due to rate limiting."""
        rate_limit_indicators = [
            "rate limit", "429", "tokens per day", "quota exceeded", 
            "rate_limit_exceeded", "too many requests"
        ]
        return any(indicator in error_message.lower() for indicator in rate_limit_indicators)
    
    def _extract_retry_delay(self, error_message: str) -> float:
        """Extract suggested retry delay from rate limit error message."""
        import re
        # Look for patterns like "try again in 1m38s" or "1m38.401999999s"
        pattern = r'try again in (\d+)m([\d.]+)s'
        match = re.search(pattern, error_message)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            return (minutes * 60) + seconds
        return self.base_delay
    
    async def _retry_with_backoff(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff retry logic and smart model switching."""
        for attempt in range(self.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)
                if attempt > 0:
                    console.print(f"SnapInfra operation successful after {attempt} retry attempts", style="green")
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                if self._is_rate_limit_error(error_msg):
                    self.rate_limit_detected = True
                    
                    # Try model switching before giving up
                    if attempt < self.max_retries:
                        # First try switching to a fallback model
                        if await self._try_model_switch(error_msg):
                            console.print(
                                f"🔄 Continuing with fallback model (attempt {attempt + 1}/{self.max_retries})", 
                                style="cyan"
                            )
                            continue
                        
                        # If no model switch available, use traditional backoff
                        suggested_delay = self._extract_retry_delay(error_msg)
                        backoff_delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        delay = min(suggested_delay, backoff_delay, 60)  # Cap at 60 seconds
                        
                        console.print(
                            f"Rate limit encountered. Retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})", 
                            style="yellow"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        console.print(
                            f"Maximum retries ({self.max_retries}) exceeded due to rate limiting", 
                            style="red"
                        )
                        break
                else:
                    # Non-rate-limit error, don't retry
                    raise e
        
        # If we get here, all retries failed
        raise Exception(f"SnapInfra operation failed after {self.max_retries} retries: {error_msg}")
    
    async def _initialize_model_switching(self):
        """Initialize model switching support for the multi-agent system."""
        try:
            # Load config
            if self.config is None:
                self.config = load_config()
            
            # Set original backend name from the backend class
            if hasattr(self.backend, '__class__'):
                if 'Groq' in self.backend.__class__.__name__:
                    self.original_backend_name = 'groq'
                elif 'OpenAI' in self.backend.__class__.__name__:
                    self.original_backend_name = 'openai'
                elif 'Bedrock' in self.backend.__class__.__name__:
                    self.original_backend_name = 'bedrock'
                elif 'Ollama' in self.backend.__class__.__name__:
                    self.original_backend_name = 'ollama'
            
            # Get available backends from config
            available_backends = list(self.config.backends.keys())
            
            # Initialize fallback models
            if self.original_backend_name:
                self.fallback_models = model_switcher.get_fallback_models(
                    self.original_model or self.model,
                    self.original_backend_name,
                    available_backends
                )
                
                if self.fallback_models:
                    console.print(f"🎯 Initialized {len(self.fallback_models)} fallback models for rate limit handling", style="dim green")
            
        except Exception as e:
            console.print(f"Could not initialize model switching: {e}", style="dim yellow")
    
    async def _try_model_switch(self, error_msg: str) -> bool:
        """Try switching to a fallback model when rate limits are hit."""
        try:
            # Load config if not already loaded
            if self.config is None:
                self.config = load_config()
            
            # Initialize fallback models if not done yet
            if not self.fallback_models:
                await self._initialize_model_switching()
                
            if not self.fallback_models and self.original_backend_name:
                available_backends = list(self.config.backends.keys())
                self.fallback_models = model_switcher.get_fallback_models(
                    self.original_model or self.model,
                    self.original_backend_name,
                    available_backends
                )
                console.print(f"🎯 Found {len(self.fallback_models)} fallback models", style="dim cyan")
            
            # Try next fallback model
            if self.current_fallback_index < len(self.fallback_models):
                new_model, new_backend = self.fallback_models[self.current_fallback_index]
                self.current_fallback_index += 1
                
                # Switch to new model/backend
                success = await self._switch_to_model(new_model, new_backend, error_msg)
                if success:
                    self.model_switches_count += 1
                    return True
            
            return False
        except Exception as e:
            console.print(f"Error during model switching: {e}", style="red")
            return False
    
    async def _switch_to_model(self, new_model: str, new_backend: str, reason: str) -> bool:
        """Switch to a new model and backend."""
        try:
            # Store original backend name if not already stored
            if self.original_backend_name is None:
                self.original_backend_name = getattr(self.backend, 'backend_name', 'unknown')
                if hasattr(self.backend, '__class__'):
                    if 'Groq' in self.backend.__class__.__name__:
                        self.original_backend_name = 'groq'
                    elif 'OpenAI' in self.backend.__class__.__name__:
                        self.original_backend_name = 'openai'
            
            # Get backend config
            backend_config = self.config.backends.get(new_backend)
            if not backend_config:
                console.print(f"Backend {new_backend} not found in config", style="red")
                return False
            
            # Create new backend
            new_backend_instance = create_backend(backend_config)
            
            # Test the new backend/model combination
            test_models = await new_backend_instance.list_models()
            if new_model not in test_models:
                console.print(f"Model {new_model} not available on {new_backend}", style="red")
                return False
            
            # Update current backend and model
            old_model = self.model
            old_backend_name = self.original_backend_name or 'unknown'
            
            self.backend = new_backend_instance
            self.model = new_model
            
            # Generate explanation
            explanation = model_switcher.explain_model_switch(
                old_model, new_model, old_backend_name, new_backend, reason
            )
            console.print(explanation, style="cyan")
            
            return True
            
        except Exception as e:
            console.print(f"Failed to switch to {new_model} on {new_backend}: {e}", style="red")
            return False
    
    def _get_model_switching_summary(self) -> str:
        """Get summary of model switches for analytics."""
        if self.model_switches_count == 0:
            return "No model switches needed"
        
        current_model = self.model
        original_model = self.original_model or "unknown"
        
        if self.model_switches_count == 1:
            return f"Switched once: {original_model} → {current_model}"
        else:
            return f"Switched {self.model_switches_count} times, ended with: {current_model}"
    
    def _get_smart_agent_assignment(self, file_path: str, file_type: str, purpose: str) -> str:
        """Intelligently assign files to the most appropriate agent based on file characteristics."""
        file_path_lower = file_path.lower()
        purpose_lower = purpose.lower()
        
        # Comprehensive agent assignment logic with top-priority IaC and Docker specialists
        assignments = {
            "iac_specialist": {
                "extensions": [".tf", ".hcl", ".yaml", ".yml", ".json", ".bicep", ".template", ".cfn", ".arm"],
                "paths": ["terraform", "iac", "infrastructure", "cloudformation", "templates", "bicep", "pulumi", "cdk", "deployment", "cloud"],
                "keywords": ["terraform", "cloudformation", "infrastructure", "iac", "aws", "azure", "gcp", "cloud", "bicep", "pulumi", "cdk", "deployment", "provision"],
                "file_types": ["config", "script"],
                "files": ["main.tf", "variables.tf", "outputs.tf", "terraform", "cloudformation", "template", "bicep", "pulumi", "cdk"]
            },
            "docker_specialist": {
                "extensions": [".dockerfile", ".dockerignore"],
                "paths": ["docker", "containers", "dockerfiles", ".docker", "compose", "k8s", "kubernetes", "helm"],
                "keywords": ["docker", "dockerfile", "container", "compose", "kubernetes", "k8s", "helm", "image", "containerization"],
                "file_types": ["config", "script"],
                "files": ["dockerfile", "docker-compose", ".dockerignore", "compose", "k8s", "kubernetes"]
            },
            "architect": {
                "extensions": [".json", ".yaml", ".toml"],
                "paths": ["architecture", "design", "planning", "specs"],
                "keywords": ["architecture", "design", "specification", "blueprint", "planning", "structure"],
                "file_types": ["config", "docs"],
                "files": ["architecture", "design-doc", "specs", "blueprint"]
            },
            "backend": {
                "extensions": [".js", ".ts", ".py", ".go", ".java", ".php", ".rb", ".cs", ".cpp", ".c", ".rs"],
                "paths": ["server", "api", "backend", "services", "controllers", "middleware", "handlers", "core"],
                "keywords": ["server", "api", "service", "controller", "middleware", "handler", "business logic", "core"],
                "file_types": ["code"]
            },
            "security": {
                "extensions": [".js", ".ts", ".py", ".go", ".java", ".php", ".rb", ".cs"],
                "paths": ["auth", "security", "middleware", "guards", "policies", "encryption", "oauth"],
                "keywords": ["auth", "security", "authentication", "authorization", "jwt", "oauth", "encryption", "validation", "sanitization"],
                "file_types": ["code"],
                "files": ["auth", "security", "middleware", "guard", "policy"]
            },
            "database": {
                "extensions": [".sql", ".js", ".ts", ".py", ".go", ".java"],
                "paths": ["models", "schemas", "migrations", "database", "db", "data", "repositories", "dao"],
                "keywords": ["model", "schema", "migration", "database", "query", "repository", "dao", "orm", "sql"],
                "file_types": ["code"],
                "files": ["model", "schema", "migration", "seed"]
            },
            "api": {
                "extensions": [".js", ".ts", ".py", ".go", ".java", ".php", ".rb", ".cs", ".yaml", ".json"],
                "paths": ["routes", "api", "endpoints", "controllers", "handlers", "openapi", "swagger"],
                "keywords": ["route", "endpoint", "api", "controller", "handler", "rest", "graphql", "openapi", "swagger"],
                "file_types": ["code", "config"],
                "files": ["routes", "api", "endpoints", "openapi", "swagger"]
            },
            "performance": {
                "extensions": [".js", ".ts", ".py", ".go", ".java", ".php", ".rb", ".cs", ".cpp"],
                "paths": ["utils", "helpers", "optimization", "cache", "performance", "algorithms"],
                "keywords": ["optimization", "performance", "cache", "algorithm", "efficiency", "benchmark", "profiling"],
                "file_types": ["code"],
                "files": ["utils", "helpers", "cache", "optimization"]
            },
            "devops": {
                "extensions": [".yml", ".yaml", ".json", ".toml", ".ini", ".conf", ".sh", ".ps1", ".tf"],
                "paths": ["docker", "deploy", "ci", "cd", "infra", "k8s", "kubernetes", "terraform", "ansible", ".github", ".gitlab"],
                "keywords": ["docker", "deploy", "build", "ci", "cd", "pipeline", "infra", "config", "environment", "kubernetes", "terraform"],
                "file_types": ["config", "script"],
                "files": ["dockerfile", "docker-compose", "makefile", "jenkinsfile", "azure-pipelines", ".github", ".gitlab", "terraform"]
            },
            "technical_writer": {
                "extensions": [".md", ".txt", ".rst", ".adoc", ".html"],
                "paths": ["docs", "documentation", "readme", "wiki", "guides", "tutorials"],
                "keywords": ["readme", "docs", "documentation", "guide", "manual", "help", "tutorial", "changelog", "contributing"],
                "file_types": ["docs"],
                "files": ["readme", "changelog", "license", "contributing", "api-docs", "guide", "tutorial"]
            },
            "code_reviewer": {
                "extensions": [".test.js", ".spec.js", ".test.ts", ".spec.ts", ".test.py", ".spec.py"],
                "paths": ["test", "tests", "spec", "specs", "__tests__", "e2e", "integration", "unit", "quality"],
                "keywords": ["test", "spec", "mock", "fixture", "e2e", "integration", "unit", "coverage", "quality", "review"],
                "file_types": ["test"],
                "files": ["test", "spec", "quality", "lint", "review"]
            }
        }
        
        # Calculate scores for each agent with priority boost for IaC and Docker specialists
        agent_scores = {}
        for agent_name, criteria in assignments.items():
            score = 0
            
            # Check file extension
            for ext in criteria.get("extensions", []):
                if file_path_lower.endswith(ext):
                    score += 3
                    break
            
            # Check path segments
            for path_segment in criteria.get("paths", []):
                if path_segment in file_path_lower:
                    score += 2
            
            # Check purpose keywords
            for keyword in criteria.get("keywords", []):
                if keyword in purpose_lower:
                    score += 2
            
            # Check file type
            if file_type in criteria.get("file_types", []):
                score += 1
            
            # Check specific filenames
            filename = os.path.basename(file_path_lower)
            for special_file in criteria.get("files", []):
                if special_file in filename:
                    score += 3
            
            # Priority boost for top-priority agents
            if agent_name in ["iac_specialist", "docker_specialist"] and score > 0:
                score += 5  # Significant priority boost for infrastructure specialists
            
            agent_scores[agent_name] = score
        
        # Return agent with highest score, default to backend if tie
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        return best_agent[0] if best_agent[1] > 0 else "backend"
    
    def _group_files_by_agent(self, file_list: List[Dict]) -> Dict[str, List[Dict]]:
        """Group files by the most appropriate agent to reduce redundant API calls."""
        agent_groups = {}
        
        for file_info in file_list:
            file_path = file_info.get('path', '')
            file_type = file_info.get('type', 'code')
            purpose = file_info.get('purpose', '')
            
            # Get the best agent for this file
            assigned_agent = self._get_smart_agent_assignment(file_path, file_type, purpose)
            
            # Add to agent's group
            if assigned_agent not in agent_groups:
                agent_groups[assigned_agent] = []
            agent_groups[assigned_agent].append(file_info)
        
        return agent_groups
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count using a simple heuristic (chars/4 approximation)."""
        return max(1, len(text) // 4)
    
    def _optimize_prompt_for_tokens(self, prompt: str, max_tokens: int = None) -> str:
        """Optimize prompt for token efficiency while preserving key information."""
        if max_tokens is None:
            max_tokens = self.max_tokens_per_request
        
        # Check cache first
        cache_key = f"{hash(prompt)}_{max_tokens}"
        if cache_key in self.compressed_prompts:
            return self.compressed_prompts[cache_key]
        
        current_tokens = self._estimate_token_count(prompt)
        
        if current_tokens <= max_tokens:
            self.compressed_prompts[cache_key] = prompt
            return prompt
        
        # Apply compression strategies
        optimized = self._apply_prompt_compression(prompt, max_tokens)
        
        # Cache the result
        self.compressed_prompts[cache_key] = optimized
        return optimized
    
    def _apply_prompt_compression(self, prompt: str, target_tokens: int) -> str:
        """Apply various compression techniques to reduce prompt size."""
        lines = prompt.strip().split('\n')
        
        # Remove excessive whitespace and blank lines
        lines = [line.strip() for line in lines if line.strip()]
        
        # Compress repetitive instructions
        compressed_lines = []
        prev_line = ""
        
        for line in lines:
            # Skip nearly identical consecutive lines
            if not self._lines_too_similar(prev_line, line):
                compressed_lines.append(line)
            prev_line = line
        
        # Join and check token count
        compressed = '\n'.join(compressed_lines)
        current_tokens = self._estimate_token_count(compressed)
        
        # If still too long, apply aggressive compression
        if current_tokens > target_tokens:
            compressed = self._aggressive_prompt_compression(compressed, target_tokens)
        
        return compressed
    
    def _lines_too_similar(self, line1: str, line2: str, threshold: float = 0.8) -> bool:
        """Check if two lines are too similar (simple similarity check)."""
        if not line1 or not line2:
            return False
        
        # Simple character-based similarity
        common_chars = sum(1 for a, b in zip(line1, line2) if a == b)
        max_len = max(len(line1), len(line2))
        
        return (common_chars / max_len) > threshold if max_len > 0 else False
    
    def _aggressive_prompt_compression(self, prompt: str, target_tokens: int) -> str:
        """Apply aggressive compression when gentle methods aren't enough."""
        lines = prompt.split('\n')
        
        # Prioritize lines containing key information
        priority_keywords = [
            'requirements:', 'generate', 'file:', 'purpose:', 'type:', 
            'tech stack', 'architecture', 'project', 'content'
        ]
        
        high_priority = []
        medium_priority = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in priority_keywords):
                high_priority.append(line)
            else:
                medium_priority.append(line)
        
        # Start with high priority lines
        result_lines = high_priority.copy()
        current_tokens = self._estimate_token_count('\n'.join(result_lines))
        
        # Add medium priority lines if we have room
        for line in medium_priority:
            test_content = '\n'.join(result_lines + [line])
            test_tokens = self._estimate_token_count(test_content)
            
            if test_tokens <= target_tokens:
                result_lines.append(line)
            else:
                break
        
        return '\n'.join(result_lines)
    
    def _create_batch_prompt(self, files: List[Dict], project_context: str) -> str:
        """Create an optimized batch prompt for multiple files."""
        if not files:
            return ""
        
        # Group similar file types for batch processing
        file_groups = {}
        for file_info in files:
            file_type = file_info.get('type', 'code')
            if file_type not in file_groups:
                file_groups[file_type] = []
            file_groups[file_type].append(file_info)
        
        batch_sections = []
        batch_sections.append(project_context)
        batch_sections.append("\nGenerate the following files:")
        
        for file_type, type_files in file_groups.items():
            if len(type_files) > 1:
                batch_sections.append(f"\n## {file_type.title()} Files:")
                for file_info in type_files:
                    batch_sections.append(
                        f"- {file_info['path']}: {file_info['purpose']}"
                    )
            else:
                file_info = type_files[0]
                batch_sections.append(
                    f"\n## {file_info['path']} ({file_type}):\n{file_info['purpose']}"
                )
        
        batch_sections.append("\nReturn each file with a clear separator: ---FILE: filename.ext---")
        
        return "\n".join(batch_sections)
    
    def _display_token_usage_analytics(self):
        """Display comprehensive token usage analytics."""
        console.print("\nToken Usage Analytics:", style="bold blue")
        console.print(f"  Estimated tokens used: {self.token_usage_estimate:,}", style="cyan")
        console.print(f"  Successful generations: {self.successful_generations}", style="green")
        console.print(f"  Failed generations: {self.failed_generations}", style="red")
        
        total_operations = self.successful_generations + self.failed_generations
        if total_operations > 0:
            success_rate = (self.successful_generations / total_operations) * 100
            console.print(f"  Success rate: {success_rate:.1f}%", style="green" if success_rate > 80 else "yellow")
            
            avg_tokens_per_success = self.token_usage_estimate / max(1, self.successful_generations)
            console.print(f"  Avg tokens per successful generation: {avg_tokens_per_success:.0f}", style="cyan")
        
        if self.rate_limit_detected:
            console.print("Rate limits encountered - consider using smaller model or upgrading quota", style="yellow")
    
    def _get_efficiency_recommendations(self) -> List[str]:
        """Get recommendations for improving token efficiency."""
        recommendations = []
        
        if self.token_usage_estimate > 50000:
            recommendations.append("Consider using a smaller model for simple files")
        
        if self.failed_generations > self.successful_generations:
            recommendations.append("High failure rate - check API keys and quotas")
        
        if self.rate_limit_detected:
            recommendations.append("Rate limits detected - enable batch processing")
            recommendations.append("Consider upgrading API plan or using multiple keys")
        
        cache_hit_potential = len(self.compressed_prompts) / max(1, self.successful_generations + self.failed_generations)
        if cache_hit_potential < 0.3:
            recommendations.append("Low prompt caching efficiency - similar files could be batched")
        
        return recommendations
    
    def _prompt_for_dockerization(self, generated_files: List[str] = None) -> bool:
        """Prompt user about dockerizing the generated project."""
        try:
            console.print("\n" + "="*80, style="bright_blue")
            console.print("PROJECT GENERATION COMPLETE!", style="bold bright_green", justify="center")
            console.print("="*80, style="bright_blue")
            
            # Display what was generated
            if generated_files:
                console.print(f"\nGenerated {len(generated_files)} files with sophisticated IAC and backend code", style="green")
                for file_path in generated_files[:5]:  # Show first 5 files
                    console.print(f"  - {file_path}", style="dim green")
                if len(generated_files) > 5:
                    console.print(f"  ... and {len(generated_files) - 5} more files", style="dim green")
            
            # Dockerization prompt
            console.print("\nDOCKERIZATION RECOMMENDATION:", style="bold bright_blue")
            console.print("Your sophisticated backend and infrastructure code would benefit from containerization!", style="yellow")
            
            dockerization_panel = Panel.fit(
                "**CONTAINERIZATION BENEFITS:**\n\n"
                "- **Deployment Consistency**: Run anywhere with Docker\n"
                "- **Environment Isolation**: Avoid dependency conflicts\n"
                "- **Scalability**: Easy horizontal scaling with orchestration\n"
                "- **DevOps Integration**: Perfect for CI/CD pipelines\n"
                "- **Production Ready**: Enterprise-grade containerization",
                title="Why Dockerize?",
                border_style="bright_cyan"
            )
            console.print(dockerization_panel)
            
            # Interactive prompt
            console.print("\nWould you like me to generate comprehensive Docker configurations?", style="bold bright_yellow")
            console.print("This will include:", style="cyan")
            console.print("  - Multi-stage Dockerfiles with optimization", style="dim cyan")
            console.print("  - Docker Compose with all services", style="dim cyan")
            console.print("  - Production-ready container configurations", style="dim cyan")
            console.print("  - Security best practices and optimization", style="dim cyan")
            
            response = console.input("\n[Y/n] Generate Docker containers? (Y=Yes, n=No): ").strip().lower()
            
            if response in ['', 'y', 'yes', 'yeah', 'yep', '1', 'true']:
                console.print("\n**EXCELLENT CHOICE!** Preparing Docker specialist for containerization...", style="bold bright_green")
                return True
            else:
                console.print("\nNo problem! Your project is ready to use without containerization.", style="bright_yellow")
                console.print("**TIP**: You can always run SnapInfra again later to add Docker containers!", style="dim yellow")
                return False
                
        except Exception as e:
            console.print(f"\nError during dockerization prompt: {e}", style="red")
            return False
    
    def _display_comprehensive_analytics(self):
        """Display comprehensive analytics including task completion and token usage."""
        console.print("\nGeneration Analytics:", style="bold blue")
        
        # Task completion analytics
        total_tasks = sum(info['total_files'] for info in self.task_checklist.values())
        total_completed = sum(info['completed'] for info in self.task_checklist.values())
        total_failed = sum(info['failed'] for info in self.task_checklist.values())
        
        analytics_table = Table(title="Agent Performance Summary")
        analytics_table.add_column("Metric", style="cyan")
        analytics_table.add_column("Value", style="green")
        
        analytics_table.add_row("Total Files Planned", str(total_tasks))
        analytics_table.add_row("Successfully Generated", str(total_completed))
        analytics_table.add_row("Failed", str(total_failed))
        
        if total_tasks > 0:
            success_rate = (total_completed / total_tasks) * 100
            analytics_table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        analytics_table.add_row("Estimated Tokens Used", f"{self.token_usage_estimate:,}")
        
        if self.successful_generations > 0:
            avg_tokens_per_success = self.token_usage_estimate / self.successful_generations
            analytics_table.add_row("Avg Tokens per File", f"{avg_tokens_per_success:.0f}")
        
        # Add model switching information
        switching_summary = self._get_model_switching_summary()
        analytics_table.add_row("Model Switching", switching_summary)
        
        console.print(analytics_table)
        
        if self.rate_limit_detected:
            console.print("Rate limits encountered - automatic model switching was attempted", style="yellow")
        
        if self.model_switches_count > 0:
            console.print(f"✨ Smart model switching helped maintain continuity ({self.model_switches_count} switches)", style="green")
    
    def _initialize_task_checklist(self, agent_groups: Dict[str, List[Dict]]):
        """Initialize the task checklist for all agents and files."""
        self.task_checklist = {}
        for agent_name, files in agent_groups.items():
            self.task_checklist[agent_name] = {
                'total_files': len(files),
                'completed': 0,
                'failed': 0,
                'current_file': None,
                'files': {f['path']: {'status': 'pending', 'details': f['purpose']} for f in files}
            }
    
    def _update_task_progress(self, agent_name: str, file_path: str, status: str, details: str = None):
        """Thread-safe update task progress for a specific file during parallel execution."""
        with self._progress_lock:
            if agent_name in self.task_checklist and file_path in self.task_checklist[agent_name]['files']:
                old_status = self.task_checklist[agent_name]['files'][file_path]['status']
                self.task_checklist[agent_name]['files'][file_path]['status'] = status
                
                if details:
                    self.task_checklist[agent_name]['files'][file_path]['details'] = details
                
                # Update counters
                if status == 'completed' and old_status != 'completed':
                    self.task_checklist[agent_name]['completed'] += 1
                elif status == 'failed' and old_status != 'failed':
                    self.task_checklist[agent_name]['failed'] += 1
                
                if status == 'generating':
                    self.task_checklist[agent_name]['current_file'] = file_path
    
    def _create_progress_display(self) -> Table:
        """Create a rich table showing current progress."""
        table = Table(title="SnapInfra Multi-Agent Generation Progress")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Progress", style="green")
        table.add_column("Current Task", style="yellow")
        table.add_column("Status", justify="center")
        
        for agent_name, progress in self.task_checklist.items():
            total = progress['total_files']
            completed = progress['completed']
            failed = progress['failed']
            
            # Progress bar
            progress_ratio = completed / total if total > 0 else 0
            progress_bar = "#" * int(progress_ratio * 10) + "-" * (10 - int(progress_ratio * 10))
            progress_text = f"{progress_bar} {completed}/{total}"
            
            # Current task
            current_task = progress.get('current_file', 'Waiting')
            if current_task and current_task != 'Waiting':
                current_task = current_task.split('/')[-1]  # Show just filename
            
            # Status
            if failed > 0:
                status = f"[red]{failed} failed[/red]"
            elif completed == total:
                status = "[green]Complete[/green]"
            else:
                status = "[yellow]Working[/yellow]"
            
            table.add_row(
                agent_name.title().replace('_', ' '),
                progress_text,
                current_task,
                status
            )
        
        return table
    
    def _create_detailed_checklist(self) -> Tree:
        """Create a detailed tree view of all tasks."""
        tree = Tree("Project Generation Checklist")
        
        for agent_name, progress in self.task_checklist.items():
            agent_node = tree.add(f"SnapInfra {agent_name.title().replace('_', ' ')} Agent")
            
            for file_path, file_info in progress['files'].items():
                status = file_info['status']
                details = file_info['details']
                
                if status == 'completed':
                    icon = "[DONE]"
                    style = "green"
                elif status == 'failed':
                    icon = "[FAIL]"
                    style = "red"
                elif status == 'generating':
                    icon = "[WORK]"
                    style = "yellow"
                else:
                    icon = "[WAIT]"
                    style = "dim"
                
                file_node = agent_node.add(f"{icon} {file_path}", style=style)
                file_node.add(f"Purpose: {details}", style="dim")
        
        return tree
    
    def _display_agent_activity(self, agent_name: str, activity: str, file_path: str = None):
        """Display what an agent is currently doing."""
        agent_display = agent_name.title().replace('_', ' ')
        
        if file_path:
            filename = file_path.split('/')[-1]
            console.print(f"  {agent_display}: {activity} -> {filename}", style="cyan")
        else:
            console.print(f"  {agent_display}: {activity}", style="cyan")
    
    def _show_live_progress_update(self):
        """Show a live progress update with current status."""
        # Clear some space and show current progress
        console.print("")
        console.print("Current Progress:", style="bold blue")
        console.print(self._create_progress_display())
        console.print("")
    
    def _display_parallel_execution_status(self, active_agents: List[str]):
        """Display current status of parallel agent execution."""
        console.print("\nParallel Execution Status:", style="bold cyan")
        
        with self._progress_lock:
            for agent_name in active_agents:
                if agent_name in self.task_checklist:
                    progress_info = self.task_checklist[agent_name]
                    current_file = progress_info.get('current_file', 'Initializing')
                    completed = progress_info['completed']
                    total = progress_info['total_files']
                    
                    if current_file and current_file != 'Initializing':
                        current_filename = current_file.split('/')[-1]
                        console.print(f"  {agent_name.title().replace('_', ' ')}: Working on {current_filename} ({completed}/{total} complete)", style="cyan")
                    else:
                        console.print(f"  {agent_name.title().replace('_', ' ')}: {current_file} ({completed}/{total} complete)", style="dim cyan")
    
    async def generate_project_collaboratively(self, user_prompt: str, project_name: str) -> Dict[str, Any]:
        """Generate a project using collaborative multi-agent approach."""
        console.print("Starting SnapInfra multi-agent project generation", style="bold blue")
        
        # Step 1: Project Architecture Planning
        with console.status("Software Architect analyzing requirements and designing project structure..."):
            architecture_prompt = f"""
            User's Specific Project Request: {user_prompt}
            Project Name: {project_name}
            
            CRITICAL: As the Project Architect, you must DEEPLY ANALYZE the user's specific requirements before generating any recommendations.
            
            FIRST, carefully analyze:
            1. What EXACTLY is the user trying to build?
            2. What specific problem are they solving?
            3. What scale/complexity does their description imply?
            4. What technologies or platforms did they mention or prefer?
            5. What constraints or requirements can you infer from their request?
            
            THEN, create a comprehensive project plan tailored SPECIFICALLY to their needs. Provide:
            
            1. Technology stack recommendation with justification
            2. High-level architecture and design patterns
            3. Complete folder structure and file organization
            4. List of 15-20 essential files to create with descriptions
            5. Infrastructure as Code (IaC) requirements for multi-cloud deployment
            6. Docker containerization and orchestration strategy
            7. Dependencies and external libraries needed
            8. Development and deployment considerations
            
            PRIORITY: Include infrastructure and containerization files as TOP PRIORITY:
            - Dockerfile and docker-compose.yml for containerization
            - Terraform/CloudFormation/Bicep files for infrastructure
            - Kubernetes manifests if applicable
            - CI/CD pipeline configurations
            
            Respond with a detailed JSON structure:
            {{
                "project_type": "web_app|api|desktop|mobile|library",
                "tech_stack": ["primary", "technologies", "list"],
                "architecture_pattern": "Description of chosen pattern",
                "folder_structure": ["folder1", "folder2/subfolder"],
                "files": [
                    {{
                        "path": "src/main.js",
                        "type": "code|config|docs|test",
                        "purpose": "Main application entry point",
                        "assigned_to": "iac_specialist|docker_specialist|backend|frontend|security|database|api|performance|devops|technical_writer|code_reviewer",
                        "priority": 1
                    }}
                ],
                "dependencies": {{
                    "runtime": ["dep1", "dep2"],
                    "development": ["dev-dep1", "dev-dep2"]
                }},
                "deployment_strategy": "Description of how to deploy",
                "next_steps": ["step1", "step2"]
            }}
            """
        
        try:
            # Use the native backend to get architecture response
            # Create a conversation with system message as the first message
            system_message = Message(
                role="system", 
                content=self.agents["architect"]["system_message"]
            )
            
            # Create conversation with system message first
            conversation = self.backend.chat(self.model, system_message)
            if conversation is None:
                console.print("Failed to create conversation with backend", style="red")
                return None
                
            # Send the architecture prompt as user message
            architecture_response = await conversation.send(architecture_prompt)
            if architecture_response is None:
                console.print("Backend returned null response", style="red")
                return None
                
            response_content = architecture_response.content if hasattr(architecture_response, 'content') else str(architecture_response)
            console.print(f"Architect response received: {len(response_content)} characters", style="dim")
                
            project_plan = self._parse_json_response(response_content)
            
            if not project_plan:
                console.print("Failed to get valid project plan from architect", style="red")
                return None
                
            console.print(f"Architecture planning complete: {len(project_plan.get('files', []))} files identified", style="green")
            
            # Step 2: Collaborative file generation with specialized agents
            return await self._generate_files_collaboratively(project_plan, user_prompt)
            
        except Exception as e:
            console.print(f"Error in collaborative generation: {e}", style="red")
            return None
    
    async def _generate_files_collaboratively(self, project_plan: Dict, user_prompt: str) -> Dict[str, Any]:
        """Generate files using specialized agents with intelligent assignment and real-time tracking."""
        console.print("SnapInfra specialized agents collaborating on file generation", style="bold blue")
        
        files_to_create = project_plan.get("files", [])
        generated_files = []
        
        # Use intelligent agent assignment
        agent_groups = self._group_files_by_agent(files_to_create)
        
        # Initialize task checklist
        self._initialize_task_checklist(agent_groups)
        
        # Display initial assignment and checklist
        console.print("\nIntelligent File Assignment:", style="bold cyan")
        for agent_name, files in agent_groups.items():
            file_paths = [f.get('path', 'unknown') for f in files]
            console.print(f"  {agent_name.upper()}: {len(files)} files", style="cyan")
            for path in file_paths[:3]:  # Show first 3 files
                console.print(f"    - {path}", style="dim cyan")
            if len(files) > 3:
                console.print(f"    - ... and {len(files) - 3} more", style="dim cyan")
        
        # Show initial detailed checklist
        console.print("")
        console.print(self._create_detailed_checklist())
        console.print("")
        
        # Generate files with TRUE PARALLEL execution - all agents work simultaneously
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Create a main progress task
            total_files = sum(len(files) for files in agent_groups.values())
            main_task = progress.add_task("Overall Progress", total=total_files)
            
            # Create agent tasks and prepare parallel execution
            agent_tasks = {}
            parallel_tasks = []
            
            console.print("\nStarting SnapInfra parallel agent execution:", style="bold green")
            
            for agent_name, agent_files in agent_groups.items():
                if not agent_files:
                    continue
                    
                # Ensure agent exists
                if agent_name not in self.agents:
                    console.print(f"Warning: Agent '{agent_name}' not found, using backend agent", style="yellow")
                    agent_name = "backend"
                
                # Create progress task for this agent
                agent_task = progress.add_task(
                    f"{agent_name.title().replace('_', ' ')} Agent", 
                    total=len(agent_files)
                )
                agent_tasks[agent_name] = agent_task
                
                # Display agent starting work
                self._display_agent_activity(agent_name, "Starting parallel file generation")
                
                # Create parallel task for this agent
                parallel_task = self._generate_agent_files_with_tracking(
                    agent_name, agent_files, project_plan, user_prompt, progress, agent_task, main_task
                )
                parallel_tasks.append((agent_name, parallel_task))
            
            # Execute all agents in parallel using asyncio.gather
            console.print(f"\nExecuting {len(parallel_tasks)} SnapInfra agents in parallel...", style="bold yellow")
            
            # Show initial parallel execution status
            active_agent_names = [name for name, _ in parallel_tasks]
            self._display_parallel_execution_status(active_agent_names)
            
            # Run all agent tasks concurrently
            results = await asyncio.gather(
                *[task for _, task in parallel_tasks],
                return_exceptions=True
            )
            
            # Process results and handle any exceptions
            for i, (agent_name, result) in enumerate(zip([name for name, _ in parallel_tasks], results)):
                if isinstance(result, Exception):
                    console.print(f"Agent {agent_name} encountered an error: {result}", style="red")
                    # Mark all files for this agent as failed
                    if agent_name in self.task_checklist:
                        for file_path in self.task_checklist[agent_name]['files']:
                            self._update_task_progress(agent_name, file_path, 'failed', f"Agent error: {str(result)[:50]}...")
                else:
                    generated_files.extend(result)
                
                # Clean up progress task
                if agent_name in agent_tasks:
                    progress.remove_task(agent_tasks[agent_name])
            
            console.print("\nParallel execution completed!", style="bold green")
        
        # Show final progress summary
        console.print("\nFinal Generation Summary:", style="bold green")
        console.print(self._create_progress_display())
        console.print(f"\nFile generation complete: {len(generated_files)} files created through intelligent agent collaboration", style="green")
        
        # Display comprehensive analytics
        self._display_comprehensive_analytics()
        
        recommendations = self._get_efficiency_recommendations()
        if recommendations:
            console.print("\nEfficiency Recommendations:", style="bold yellow")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"  {i}. {rec}", style="yellow")
        
        # Prompt for dockerization after successful generation
        generated_file_paths = [f.get('path', 'unknown') for f in generated_files]
        should_dockerize = self._prompt_for_dockerization(generated_file_paths)
        
        # If user wants dockerization, generate Docker files
        if should_dockerize:
            console.print("\n**DOCKERIZATION STARTING** - Preparing container configurations...", style="bold bright_green")
            
            # Generate Docker-related files using docker_specialist agent
            docker_files_to_create = [
                {
                    "path": "Dockerfile",
                    "type": "config",
                    "purpose": "Multi-stage production-ready Docker container configuration with security best practices",
                    "assigned_to": "docker_specialist",
                    "priority": 1
                },
                {
                    "path": "docker-compose.yml",
                    "type": "config",
                    "purpose": "Complete docker-compose configuration with all services, networks, and volumes",
                    "assigned_to": "docker_specialist",
                    "priority": 1
                },
                {
                    "path": ".dockerignore",
                    "type": "config",
                    "purpose": "Docker build context optimization and security configuration",
                    "assigned_to": "docker_specialist",
                    "priority": 2
                },
                {
                    "path": "docker-compose.prod.yml",
                    "type": "config",
                    "purpose": "Production-ready docker-compose override with advanced configurations",
                    "assigned_to": "docker_specialist",
                    "priority": 2
                }
            ]
            
            try:
                # Generate Docker files using the docker specialist
                docker_results = await self._generate_agent_files(
                    "docker_specialist", 
                    docker_files_to_create, 
                    project_plan, 
                    f"{user_prompt}\n\nCONTAINERIZATION CONTEXT: Generate Docker configurations for the above project with all generated files."
                )
                
                if docker_results:
                    generated_files.extend(docker_results)
                    console.print(f"\n**DOCKERIZATION COMPLETE!** Generated {len(docker_results)} container configuration files", style="bold bright_green")
                    for docker_file in docker_results:
                        console.print(f"  [SUCCESS] {docker_file.get('path', 'unknown')}", style="bright_green")
                else:
                    console.print("\nDockerization failed - no container files generated", style="yellow")
                    
            except Exception as e:
                console.print(f"\nError during dockerization: {e}", style="red")
        
        return {
            **project_plan,
            "generated_files": generated_files,
            "generation_method": "multi_agent_intelligent",
            "dockerization_applied": should_dockerize,
            "analytics": {
                "token_usage_estimate": self.token_usage_estimate,
                "successful_generations": self.successful_generations,
                "failed_generations": self.failed_generations,
                "rate_limit_detected": self.rate_limit_detected,
                "efficiency_recommendations": recommendations
            }
        }
    
    async def _generate_agent_files(self, agent_name: str, file_list: List[Dict], project_plan: Dict, user_prompt: str) -> List[Dict]:
        """Generate files using a specific specialized agent."""
        if not file_list or agent_name not in self.agents:
            return []
        
        agent = self.agents[agent_name]
        generated_files = []
        
        for file_info in file_list:
            try:
                # Create detailed prompt for the specialized agent
                generation_prompt = f"""
                Project: {user_prompt}
                Tech Stack: {', '.join(project_plan.get('tech_stack', []))}
                Architecture: {project_plan.get('architecture_pattern', 'Standard')}
                
                Generate the complete content for this file:
                
                File: {file_info['path']}
                Purpose: {file_info['purpose']}
                Type: {file_info['type']}
                
                Requirements:
                1. Generate ONLY the file content, no explanations
                2. Make it production-ready and follow best practices
                3. Include proper error handling and documentation
                4. Ensure compatibility with the chosen tech stack
                5. Consider security, performance, and maintainability
                
                Project Context: {project_plan.get('project_type', 'application')} using {project_plan.get('tech_stack', [])}
                """
                
                # Use native backend with agent's system message
                system_message = Message(
                    role="system",
                    content=agent["system_message"]
                )
                
                # Create conversation and get response
                conversation = self.backend.chat(self.model, system_message)
                if conversation is None:
                    console.print(f"Failed to create conversation for {agent_name}", style="red")
                    continue
                    
                response = await conversation.send(generation_prompt)
                content = response.content.strip() if hasattr(response, 'content') else str(response).strip()
                    
                if content:
                    # Clean up any markdown code blocks
                    content = self._clean_code_content(content)
                    
                    generated_files.append({
                        **file_info,
                        "content": content,
                        "generated_by": agent_name
                    })
                
            except Exception as e:
                console.print(f"Agent {agent_name} failed to generate {file_info['path']}: {e}", style="red")
                continue
        
        return generated_files
    
    async def _generate_agent_files_with_intelligence(self, agent_name: str, file_list: List[Dict], project_plan: Dict, user_prompt: str) -> List[Dict]:
        """Generate files using a specific agent with intelligent retry logic and batching."""
        if not file_list or agent_name not in self.agents:
            return []
        
        agent = self.agents[agent_name]
        generated_files = []
        
        # Process files in batches to be rate-limit friendly
        batch_size = 2  # Process 2 files per agent at a time
        
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i + batch_size]
            
            # Generate files in this batch concurrently
            batch_tasks = []
            for file_info in batch:
                task = self._generate_single_file_with_intelligence(agent_name, agent, file_info, project_plan, user_prompt)
                batch_tasks.append(task)
            
            # Execute batch with retry logic
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process batch results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    file_info = batch[j]
                    self.failed_generations += 1
                    console.print(f"Agent {agent_name} failed to generate {file_info['path']}: {result}", style="red")
                else:
                    generated_files.append(result)
                    self.successful_generations += 1
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(file_list):
                await asyncio.sleep(0.5)
        
        return generated_files
    
    async def _generate_agent_files_with_tracking(self, agent_name: str, file_list: List[Dict], project_plan: Dict, user_prompt: str, progress, agent_task, main_task) -> List[Dict]:
        """Generate files using a specific agent with detailed progress tracking."""
        if not file_list or agent_name not in self.agents:
            return []
        
        agent = self.agents[agent_name]
        generated_files = []
        
        # Process files in batches to be rate-limit friendly
        batch_size = 2  # Process 2 files per agent at a time
        
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i + batch_size]
            
            # Generate files in this batch with detailed tracking
            for file_info in batch:
                file_path = file_info['path']
                
                # Update task status to generating
                self._update_task_progress(agent_name, file_path, 'generating')
                self._display_agent_activity(agent_name, "Analyzing requirements and generating", file_path)
                
                try:
                    # Generate the file with intelligence
                    result = await self._generate_single_file_with_intelligence(
                        agent_name, agent, file_info, project_plan, user_prompt
                    )
                    
                    # Update progress on success
                    generated_files.append(result)
                    self.successful_generations += 1
                    
                    # Update task tracking
                    self._update_task_progress(agent_name, file_path, 'completed', f"Generated {len(result.get('content', ''))} characters")
                    self._display_agent_activity(agent_name, "Successfully generated", file_path)
                    
                    # Update progress bars
                    progress.advance(agent_task)
                    progress.advance(main_task)
                    
                except Exception as e:
                    # Update progress on failure
                    self.failed_generations += 1
                    
                    # Update task tracking
                    self._update_task_progress(agent_name, file_path, 'failed', f"Error: {str(e)[:100]}...")
                    console.print(f"Agent {agent_name} failed to generate {file_path}: {e}", style="red")
                    
                    # Still advance progress bars to keep count accurate
                    progress.advance(agent_task)
                    progress.advance(main_task)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(file_list):
                await asyncio.sleep(0.5)
        
        # Display completion message for this agent
        completed_count = self.task_checklist[agent_name]['completed']
        failed_count = self.task_checklist[agent_name]['failed']
        self._display_agent_activity(agent_name, f"Completed {completed_count} files, {failed_count} failed")
        
        return generated_files
    
    async def _generate_single_file_with_intelligence(self, agent_name: str, agent: Dict, file_info: Dict, project_plan: Dict, user_prompt: str) -> Dict:
        """Generate a single file with intelligent retry and error handling."""
        # Create base prompt
        base_prompt = f"""
        User's Specific Project Request: {user_prompt}
        
        CRITICAL ANALYSIS REQUIRED:
        - Analyze the user's EXACT requirements and problem statement
        - Identify the specific use case and business logic needed
        - Determine the appropriate complexity level for this specific project
        - Consider the user's implied technical requirements and constraints
        
        Tech Stack: {', '.join(project_plan.get('tech_stack', []))}
        Architecture: {project_plan.get('architecture_pattern', 'Standard')}
        
        Generate the complete content for this file SPECIFICALLY tailored to the user's requirements:
        
        File: {file_info['path']}
        Purpose: {file_info['purpose']}
        Type: {file_info['type']}
        
        Requirements:
        1. Generate ONLY the file content that serves the user's SPECIFIC needs
        2. Include ONLY features and functionality relevant to the user's project
        3. Use configurations and settings appropriate to the user's use case
        4. Implement business logic that matches the user's specific requirements
        5. Include error handling appropriate to the user's application type
        6. Add documentation that helps with the user's specific implementation
        7. Ensure all code serves the user's stated or implied project goals
        
        Project Context: {project_plan.get('project_type', 'application')} using {project_plan.get('tech_stack', [])}
        
        CRITICAL: Every line of code must be justified by and tailored to the user's specific project requirements. Do not include generic or boilerplate code that doesn't serve the user's specific needs.
        """
        
        # Optimize prompt for token efficiency
        generation_prompt = self._optimize_prompt_for_tokens(base_prompt)
        
        # Track token usage
        estimated_tokens = self._estimate_token_count(generation_prompt)
        self.token_usage_estimate += estimated_tokens
        
        async def generate_operation():
            # Use native backend with agent's system message
            system_message = Message(
                role="system",
                content=agent["system_message"]
            )
            
            # Create conversation and get response
            conversation = self.backend.chat(self.model, system_message)
            if conversation is None:
                raise Exception(f"Failed to create conversation for {agent_name}")
                
            response = await conversation.send(generation_prompt)
            content = response.content.strip() if hasattr(response, 'content') else str(response).strip()
                
            if not content:
                raise Exception("Empty response from agent")
            
            # Clean up any markdown code blocks
            content = self._clean_code_content(content)
            
            return {
                **file_info,
                "content": content,
                "generated_by": agent_name
            }
        
        # Execute with retry logic
        return await self._retry_with_backoff(generate_operation)
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """Parse JSON from agent response with improved handling."""
        if not response_text or not response_text.strip():
            console.print("Empty response from architect", style="red")
            return None
            
        try:
            import re
            
            console.print(f"Parsing architect response: {len(response_text)} characters", style="dim")
            
            # Try direct JSON parsing first
            try:
                parsed = json.loads(response_text.strip())
                console.print("Direct JSON parsing successful", style="green")
                return parsed
            except json.JSONDecodeError as e:
                console.print(f"Direct parsing failed: {e}", style="yellow")
            
            # Clean the response text first
            cleaned_text = self._clean_response_for_json(response_text)
            
            # Try parsing the cleaned text
            try:
                parsed = json.loads(cleaned_text)
                console.print("Cleaned JSON parsing successful", style="green")
                return parsed
            except json.JSONDecodeError as e:
                console.print(f"Cleaned parsing failed: {e}", style="yellow")
            
            # Try to find JSON in the response with improved patterns
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # JSON in code blocks
                r'```\s*([\s\S]*?)\s*```',  # Any code block
                r'({[\s\S]*})',  # Most permissive - find any JSON object
            ]
            
            for i, pattern in enumerate(json_patterns, 1):
                console.print(f"Trying JSON extraction pattern {i}...", style="dim")
                matches = re.finditer(pattern, response_text, re.DOTALL)
                
                for match in matches:
                    json_text = match.group(1) if match.groups() else match.group(0)
                    json_text = json_text.strip()
                    
                    # Skip if the match is too small to be meaningful
                    if len(json_text) < 10:
                        continue
                    
                    console.print(f"Found JSON candidate ({len(json_text)} chars): {json_text[:100]}...", style="dim")
                    
                    try:
                        # Additional cleaning for this specific JSON
                        cleaned_json = self._fix_common_json_issues(json_text)
                        parsed = json.loads(cleaned_json)
                        
                        # Validate it's a meaningful project plan
                        if self._validate_project_plan(parsed):
                            console.print(f"JSON parsing successful with pattern {i}", style="green")
                            return parsed
                        else:
                            console.print(f"JSON parsed but invalid project structure", style="yellow")
                            
                    except json.JSONDecodeError as e:
                        console.print(f"JSON parse error: {e}", style="dim yellow")
                        continue
            
            # Last resort: try to extract key-value pairs and build JSON
            console.print("Attempting key-value extraction as final fallback...", style="yellow")
            extracted_data = self._extract_key_values_from_text(response_text)
            if extracted_data and len(extracted_data) > 2:
                console.print("Successfully extracted project data from text", style="green")
                return extracted_data
            
            # Only create fallback if all else fails
            console.print("All JSON parsing attempts failed, using fallback", style="yellow")
            return self._create_smart_fallback_project_plan(response_text)
            
        except Exception as e:
            console.print(f"Error parsing JSON response: {e}", style="red")
            return self._create_smart_fallback_project_plan(response_text)
    
    def _clean_response_for_json(self, text: str) -> str:
        """Clean response text to make it more likely to parse as JSON."""
        import re
        
        # Remove common prefixes/suffixes that AIs add
        text = re.sub(r'^\s*Here\'s.*?:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\s*Based on.*?:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\s*I\'ll.*?:\s*', '', text, flags=re.IGNORECASE)
        
        # Remove trailing explanations
        text = re.sub(r'\n\nThis.*?$', '', text, flags=re.DOTALL)
        text = re.sub(r'\n\nThe above.*?$', '', text, flags=re.DOTALL)
        
        return text.strip()
    
    def _fix_common_json_issues(self, json_text: str) -> str:
        """Fix common JSON formatting issues from AI responses."""
        import re
        
        # Fix trailing commas
        json_text = re.sub(r',\s*([}\]])', r'\1', json_text)
        
        # Fix single quotes to double quotes
        json_text = re.sub(r"'([^']*?)'", r'"\1"', json_text)
        
        # Fix unquoted keys
        json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_text)
        
        return json_text
    
    def _validate_project_plan(self, data: Dict) -> bool:
        """Validate that parsed JSON looks like a valid project plan."""
        if not isinstance(data, dict):
            return False
        
        # Check for required fields that indicate a project plan
        required_indicators = ['files', 'project_type', 'tech_stack']
        has_indicators = any(key in data for key in required_indicators)
        
        if not has_indicators:
            return False
        
        # If it has files, make sure they're meaningful
        if 'files' in data:
            files = data['files']
            if not isinstance(files, list) or len(files) < 2:
                return False
            
            # Check that files have required structure
            for file_info in files:
                if not isinstance(file_info, dict) or 'path' not in file_info:
                    return False
        
        return True
    
    def _extract_key_values_from_text(self, text: str) -> Optional[Dict]:
        """Extract key-value pairs from text when JSON parsing fails completely."""
        import re
        
        extracted = {}
        
        # Try to extract project type
        project_type_match = re.search(r'project[_\s]*type["\s]*[:=]["\s]*([^"\n,}]+)', text, re.IGNORECASE)
        if project_type_match:
            extracted['project_type'] = project_type_match.group(1).strip('"\' \t')
        
        # Try to extract tech stack
        tech_stack_match = re.search(r'tech[_\s]*stack["\s]*[:=]\s*\[([^\]]+)\]', text, re.IGNORECASE)
        if tech_stack_match:
            tech_items = re.findall(r'"([^"]+)"', tech_stack_match.group(1))
            if tech_items:
                extracted['tech_stack'] = tech_items
        
        # Try to extract file paths
        file_matches = re.findall(r'["\']path["\']\s*[:=]\s*["\']([^"\',]+)["\']', text, re.IGNORECASE)
        if file_matches:
            files = []
            for i, path in enumerate(file_matches):
                files.append({
                    'path': path,
                    'type': self._guess_file_type(path),
                    'purpose': f"Generated file {i+1}",
                    'priority': i + 1
                })
            extracted['files'] = files
        
        return extracted if len(extracted) > 0 else None
    
    def _guess_file_type(self, file_path: str) -> str:
        """Guess file type based on extension and path."""
        path_lower = file_path.lower()
        
        if any(ext in path_lower for ext in ['.md', '.txt', '.rst']):
            return 'docs'
        elif any(ext in path_lower for ext in ['.json', '.yml', '.yaml', '.toml', '.env']):
            return 'config'
        elif any(ext in path_lower for ext in ['.test.', '.spec.', 'test/', 'tests/']):
            return 'test'
        elif 'dockerfile' in path_lower or 'docker-compose' in path_lower:
            return 'docker'
        elif any(ext in path_lower for ext in ['.tf', '.hcl', 'terraform']):
            return 'iac'
        else:
            return 'code'
    
    def _create_smart_fallback_project_plan(self, response_text: str) -> Dict[str, Any]:
        """Create a smarter fallback based on the user's actual request."""
        console.print("Creating smart fallback project structure based on user input", style="blue")
        
        # Try to infer project type from response
        response_lower = response_text.lower()
        
        # Social media / Facebook clone detection
        if any(term in response_lower for term in ['facebook', 'social', 'clone', 'social media', 'social network']):
            return self._create_social_media_project_plan()
        
        # E-commerce detection
        elif any(term in response_lower for term in ['ecommerce', 'e-commerce', 'shop', 'store', 'marketplace']):
            return self._create_ecommerce_project_plan()
        
        # Blog detection
        elif any(term in response_lower for term in ['blog', 'cms', 'content management']):
            return self._create_blog_project_plan()
        
        # API detection
        elif any(term in response_lower for term in ['api', 'rest', 'graphql', 'microservice']):
            return self._create_api_project_plan()
        
        # Dashboard detection
        elif any(term in response_lower for term in ['dashboard', 'admin', 'analytics']):
            return self._create_dashboard_project_plan()
        
        # Default web app fallback
        else:
            return self._create_default_web_app_plan()
    
    def _create_social_media_project_plan(self) -> Dict[str, Any]:
        """Create a Facebook/social media clone project plan."""
        return {
            "project_type": "social_media_app",
            "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Socket.io", "JWT", "Cloudinary"],
            "architecture_pattern": "Full-stack social media platform with real-time features",
            "folder_structure": ["client", "server", "shared", "uploads", "tests"],
            "files": [
                {"path": "client/src/App.js", "type": "code", "purpose": "Main React application component", "assigned_to": "frontend", "priority": 1},
                {"path": "client/src/components/Feed.js", "type": "code", "purpose": "News feed component", "assigned_to": "frontend", "priority": 1},
                {"path": "client/src/components/Post.js", "type": "code", "purpose": "Individual post component", "assigned_to": "frontend", "priority": 1},
                {"path": "client/src/components/Profile.js", "type": "code", "purpose": "User profile component", "assigned_to": "frontend", "priority": 2},
                {"path": "client/src/components/Auth/Login.js", "type": "code", "purpose": "Login component", "assigned_to": "frontend", "priority": 2},
                {"path": "client/src/components/Auth/Register.js", "type": "code", "purpose": "Registration component", "assigned_to": "frontend", "priority": 2},
                {"path": "server/index.js", "type": "code", "purpose": "Express server entry point", "assigned_to": "backend", "priority": 1},
                {"path": "server/routes/auth.js", "type": "code", "purpose": "Authentication routes", "assigned_to": "api", "priority": 1},
                {"path": "server/routes/posts.js", "type": "code", "purpose": "Post-related API routes", "assigned_to": "api", "priority": 1},
                {"path": "server/routes/users.js", "type": "code", "purpose": "User management routes", "assigned_to": "api", "priority": 2},
                {"path": "server/models/User.js", "type": "code", "purpose": "User data model", "assigned_to": "database", "priority": 1},
                {"path": "server/models/Post.js", "type": "code", "purpose": "Post data model", "assigned_to": "database", "priority": 1},
                {"path": "server/models/Comment.js", "type": "code", "purpose": "Comment data model", "assigned_to": "database", "priority": 2},
                {"path": "server/middleware/auth.js", "type": "code", "purpose": "Authentication middleware", "assigned_to": "backend", "priority": 2},
                {"path": "server/socket/socketHandlers.js", "type": "code", "purpose": "Real-time messaging handlers", "assigned_to": "backend", "priority": 3},
                {"path": "client/package.json", "type": "config", "purpose": "Frontend dependencies", "assigned_to": "frontend", "priority": 1},
                {"path": "server/package.json", "type": "config", "purpose": "Backend dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "docker-compose.yml", "type": "config", "purpose": "Multi-service Docker setup", "assigned_to": "docker_specialist", "priority": 2},
                {"path": "Dockerfile.client", "type": "config", "purpose": "Frontend Docker container", "assigned_to": "docker_specialist", "priority": 2},
                {"path": "Dockerfile.server", "type": "config", "purpose": "Backend Docker container", "assigned_to": "docker_specialist", "priority": 2},
                {"path": "client/src/styles/App.css", "type": "code", "purpose": "Main application styles", "assigned_to": "frontend", "priority": 3},
                {"path": "README.md", "type": "docs", "purpose": "Project documentation", "assigned_to": "technical_writer", "priority": 2},
                {"path": "server/tests/auth.test.js", "type": "test", "purpose": "Authentication tests", "assigned_to": "code_reviewer", "priority": 3},
                {"path": ".env.example", "type": "config", "purpose": "Environment variables template", "assigned_to": "devops", "priority": 2},
                {"path": "terraform/main.tf", "type": "iac", "purpose": "Cloud infrastructure setup", "assigned_to": "iac_specialist", "priority": 3}
            ],
            "dependencies": {
                "frontend": ["react", "react-dom", "axios", "socket.io-client", "react-router-dom"],
                "backend": ["express", "mongoose", "jsonwebtoken", "bcryptjs", "socket.io", "multer", "cors"]
            },
            "deployment_strategy": "Containerized deployment with separate frontend/backend services"
        }
    
    def _create_ecommerce_project_plan(self) -> Dict[str, Any]:
        """Create an e-commerce project plan."""
        return {
            "project_type": "ecommerce_app",
            "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Stripe", "JWT"],
            "architecture_pattern": "Full-stack e-commerce platform with payment integration",
            "files": [
                {"path": "frontend/src/App.js", "type": "code", "purpose": "Main React application", "assigned_to": "frontend", "priority": 1},
                {"path": "frontend/src/components/ProductList.js", "type": "code", "purpose": "Product listing component", "assigned_to": "frontend", "priority": 1},
                {"path": "frontend/src/components/Cart.js", "type": "code", "purpose": "Shopping cart component", "assigned_to": "frontend", "priority": 1},
                {"path": "backend/server.js", "type": "code", "purpose": "Express server", "assigned_to": "backend", "priority": 1},
                {"path": "backend/routes/products.js", "type": "code", "purpose": "Product API routes", "assigned_to": "api", "priority": 1},
                {"path": "backend/routes/orders.js", "type": "code", "purpose": "Order management routes", "assigned_to": "api", "priority": 1},
                {"path": "backend/models/Product.js", "type": "code", "purpose": "Product data model", "assigned_to": "database", "priority": 1},
                {"path": "backend/models/Order.js", "type": "code", "purpose": "Order data model", "assigned_to": "database", "priority": 1},
                {"path": "package.json", "type": "config", "purpose": "Dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "README.md", "type": "docs", "purpose": "Documentation", "assigned_to": "technical_writer", "priority": 2}
            ]
        }
    
    def _create_blog_project_plan(self) -> Dict[str, Any]:
        """Create a blog/CMS project plan."""
        return {
            "project_type": "blog_cms",
            "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Markdown"],
            "files": [
                {"path": "src/App.js", "type": "code", "purpose": "Main application", "assigned_to": "frontend", "priority": 1},
                {"path": "src/components/BlogPost.js", "type": "code", "purpose": "Blog post component", "assigned_to": "frontend", "priority": 1},
                {"path": "server/routes/posts.js", "type": "code", "purpose": "Post API", "assigned_to": "api", "priority": 1},
                {"path": "server/models/Post.js", "type": "code", "purpose": "Post model", "assigned_to": "database", "priority": 1},
                {"path": "package.json", "type": "config", "purpose": "Dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "README.md", "type": "docs", "purpose": "Documentation", "assigned_to": "technical_writer", "priority": 2}
            ]
        }
    
    def _create_api_project_plan(self) -> Dict[str, Any]:
        """Create an API project plan."""
        return {
            "project_type": "rest_api",
            "tech_stack": ["Node.js", "Express", "MongoDB", "JWT", "OpenAPI"],
            "files": [
                {"path": "src/server.js", "type": "code", "purpose": "API server", "assigned_to": "backend", "priority": 1},
                {"path": "src/routes/api.js", "type": "code", "purpose": "API routes", "assigned_to": "api", "priority": 1},
                {"path": "src/models/index.js", "type": "code", "purpose": "Data models", "assigned_to": "database", "priority": 1},
                {"path": "package.json", "type": "config", "purpose": "Dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "README.md", "type": "docs", "purpose": "API documentation", "assigned_to": "technical_writer", "priority": 1}
            ]
        }
    
    def _create_dashboard_project_plan(self) -> Dict[str, Any]:
        """Create a dashboard project plan."""
        return {
            "project_type": "dashboard_app",
            "tech_stack": ["React", "D3.js", "Node.js", "Express", "MongoDB"],
            "files": [
                {"path": "src/App.js", "type": "code", "purpose": "Dashboard application", "assigned_to": "frontend", "priority": 1},
                {"path": "src/components/Chart.js", "type": "code", "purpose": "Chart component", "assigned_to": "frontend", "priority": 1},
                {"path": "server/api/analytics.js", "type": "code", "purpose": "Analytics API", "assigned_to": "api", "priority": 1},
                {"path": "package.json", "type": "config", "purpose": "Dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "README.md", "type": "docs", "purpose": "Documentation", "assigned_to": "technical_writer", "priority": 2}
            ]
        }
    
    def _create_default_web_app_plan(self) -> Dict[str, Any]:
        """Create a default web app project plan."""
        return {
            "project_type": "web_app",
            "tech_stack": ["React", "Node.js", "Express", "MongoDB"],
            "files": [
                {"path": "src/App.js", "type": "code", "purpose": "Main application", "assigned_to": "frontend", "priority": 1},
                {"path": "server/index.js", "type": "code", "purpose": "Server entry point", "assigned_to": "backend", "priority": 1},
                {"path": "package.json", "type": "config", "purpose": "Dependencies", "assigned_to": "backend", "priority": 1},
                {"path": "README.md", "type": "docs", "purpose": "Documentation", "assigned_to": "technical_writer", "priority": 2}
            ]
        }
    
    def _create_fallback_project_plan(self, response_text: str) -> Dict[str, Any]:
        """Legacy fallback - redirect to smart fallback."""
        return self._create_smart_fallback_project_plan(response_text)
    
    def _clean_code_content(self, content: str) -> str:
        """Clean up code content by removing markdown formatting."""
        import re
        
        # Remove markdown code block formatting
        code_block_pattern = r'^```[\w]*\n?([\s\S]*?)\n?```$'
        match = re.match(code_block_pattern, content.strip(), re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return content.strip()
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Model client cleanup is handled automatically
            console.print("Multi-agent system cleanup complete", style="green")
        except Exception as e:
            console.print(f"Warning: Cleanup error: {e}", style="yellow")
