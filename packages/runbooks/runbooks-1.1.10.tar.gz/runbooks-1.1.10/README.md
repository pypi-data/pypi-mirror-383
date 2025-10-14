# 🚀 CloudOps Runbooks - Enterprise AWS Automation

[![PyPI](https://img.shields.io/pypi/v/runbooks)](https://pypi.org/project/runbooks/)
[![Python](https://img.shields.io/pypi/pyversions/runbooks)](https://pypi.org/project/runbooks/)
[![License](https://img.shields.io/pypi/l/runbooks)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen)](https://cloudops.oceansoft.io/runbooks/)
[![Downloads](https://img.shields.io/pypi/dm/runbooks)](https://pypi.org/project/runbooks/)

> **Enterprise-Grade Production-Ready AWS automation toolkit for DevOps and SRE teams managing Multi-Account Hybrid-Cloud environments at Scale** 🏢⚡

**Quick Value**: Discover, analyze, and optimize AWS resources across multi-account AWS environments with production-validated automation patterns.

---

## Runbooks FinOps & AWS MCP Servers

> The hybrid approach (Runbooks FinOps & AWS MCPs) leverages the strengths of both solutions: AWS MCPs for real-time accuracy data access and Runbooks FinOps for business intelligence and visualization, ensuring optimal cost optimization results for your enterprise environment.

---

## 🏆 **5-Minute Manager Success Path**

### **Step 1: Installation** (30 seconds)
```bash
pip install runbooks
runbooks --version
```

### **Step 2: Cost Discovery** (3 minutes)
```bash
# Replace with your billing profile
export AWS_BILLING_PROFILE="your-billing-readonly-profile"
runbooks finops --dry-run --profile $AWS_BILLING_PROFILE

# Expected output: Cost optimization opportunities across multiple categories
```

### **Step 3: Executive Reports** (90 seconds)
```bash
runbooks finops --export pdf --report-name executive-summary
runbooks finops --export csv --detailed-analysis
```

## 🎯 Why CloudOps Runbooks?

| Feature | Benefit | Status |
|---------|---------|--------|
| 🤖 **AI-Agents Orchestration** | AI-Agents FAANG SDLC coordination | ✅ Production Ready |
| ⚡ **Blazing Performance** | Sub-second CLI responses | ✅ 0.11s execution |
| 💰 **Cost Analysis** | Multi-account cost monitoring | ✅ Real-time analysis |
| 🔒 **Enterprise Security** | Zero-trust, compliance ready | ✅ SOC2, PCI-DSS, HIPAA |
| 🏗️ **Multi-Account Ready** | Universal AWS integration | ✅ 200+ accounts supported |
| 📊 **Rich Reporting** | Executive + technical dashboards | ✅ 15+ output formats |

## 💰 **Strategic Value Framework**

### **Business Impact Matrix**
```bash
# Enterprise cost optimization suite
pip install runbooks

# Business scenario analysis
runbooks finops --scenario workspaces --dry-run
runbooks finops --scenario nat-gateway --dry-run
runbooks finops --scenario elastic-ip --dry-run
runbooks finops --scenario rds-snapshots --dry-run
runbooks finops --scenario ebs-volumes --dry-run

# Strategic analysis modes
runbooks finops --profile $AWS_BILLING_PROFILE            # Cost visibility
runbooks finops --trend --profile $AWS_BILLING_PROFILE    # Trend analysis
runbooks finops --audit --profile $AWS_BILLING_PROFILE    # Audit compliance
```

### **Executive-Ready Deliverables**
| Scenario | Time to Value | Deliverable |
|----------|---------------|-------------|
| 🏢 **WorkSpaces Optimization** | 2 minutes | Executive PDF report |
| 🌐 **Network Cost Reduction** | 3 minutes | Cost analysis dashboard |
| 📊 **Storage Efficiency** | 2 minutes | Optimization roadmap |
| 🎯 **Complete Cost Audit** | 5 minutes | Comprehensive analysis |

## 📦 Installation & Quick Start

### Production Installation
```bash
pip install runbooks

# Verify installation
runbooks --help
runbooks inventory collect --help
```

### Configuration
```bash
# Set up your AWS profiles
export AWS_BILLING_PROFILE="your-billing-readonly-profile"
export AWS_MANAGEMENT_PROFILE="your-management-readonly-profile"
export AWS_OPERATIONS_PROFILE="your-operations-readonly-profile"

# Test single account access
runbooks inventory collect --profile $AWS_OPERATIONS_PROFILE --regions us-east-1
```

## 🧰 Core Modules

| Module | Purpose | Key Commands | Business Value |
|--------|---------|--------------|----------------|
| 📊 **Inventory** | Multi-account resource discovery | `runbooks inventory collect` | Complete visibility across 50+ services |
| 💰 **FinOps** | Multi-account cost analysis | `runbooks finops` | Real-time cost optimization |
| 🔒 **Security** | Compliance & baseline testing | `runbooks security assess` | 15+ security checks, 4 languages |
| 🏛️ **CFAT** | Cloud Foundations Assessment | `runbooks cfat assess` | Executive-ready compliance reports |
| ⚙️ **Operate** | Resource lifecycle management | `runbooks operate ec2 start` | Safe resource operations |
| 🔗 **VPC** | Network analysis & optimization | `runbooks vpc analyze` | Network cost optimization |
| 🏢 **Organizations** [PLANNED] | OU structure management | Coming in v1.2 | Landing Zone automation |
| 🛠️ **Remediation** [PLANNED] | Automated security fixes | Coming in v1.2 | 50+ security playbooks |

## ⚡ Essential Commands Reference

### 🔍 Discovery & Inventory
```bash
# Multi-service resource discovery
runbooks inventory collect -r ec2,s3,rds --profile production

# Cross-account organization scan
runbooks scan --all-accounts --include-cost-analysis

# Specialized discovery operations
runbooks inventory collect -r lambda --include-code-analysis
```

### 💰 Cost Management
```bash
# Interactive cost dashboard
runbooks finops --profile your-billing-profile

# Cost optimization analysis
runbooks finops --optimize --target-savings 30

# Multi-account cost aggregation
runbooks finops --all-accounts --breakdown-by service,account,region
```

### 🔒 Security & Compliance
```bash
# Security baseline assessment
runbooks security assess --profile production --language EN

# Multi-framework compliance check
runbooks cfat assess --compliance-framework "AWS Well-Architected"

# Specialized security operations
runbooks security check root_mfa --profile management
```

### ⚙️ Resource Operations
```bash
# Safe EC2 operations (dry-run by default)
runbooks operate ec2 stop --instance-ids i-1234567890abcdef0 --dry-run

# S3 security hardening
runbooks operate s3 set-public-access-block --account-id 123456789012

# CloudFormation operations
runbooks operate cloudformation move-stack-instances \
  --source-stackset old-baseline --target-stackset new-baseline --dry-run
```

### 🎨 CLI Parameter Flexibility (v1.1.10+)

**Enhanced UX**: All commands now support flexible format specification with **short flag support**

#### Triple Alias Pattern
Choose your preferred parameter style - all forms work identically:

| Style | Example | Use Case |
|-------|---------|----------|
| **Short** ✨ | `-f json` | Interactive CLI (save keystrokes) |
| **Standard** | `--format json` | Scripts & automation |
| **Legacy** | `--export-format json` | Backward compatibility |

#### Examples - All Three Forms Work

**Organization Visualization**:
```bash
# All three commands produce identical output
runbooks inventory draw-org -f graphviz --profile $MANAGEMENT_PROFILE
runbooks inventory draw-org --format graphviz --profile $MANAGEMENT_PROFILE
runbooks inventory draw-org --export-format graphviz --profile $MANAGEMENT_PROFILE
```

**Cost Analysis Export**:
```bash
# Choose your preferred style
runbooks finops analyze -f csv --profile $BILLING_PROFILE
runbooks finops analyze --format csv --profile $BILLING_PROFILE
runbooks finops analyze --export-format csv --profile $BILLING_PROFILE
```

**Account Inventory**:
```bash
# Short form for interactive use (NEW in v1.1.10)
runbooks inventory list-org-accounts -f json --output accounts.json

# Standard form for scripts
runbooks inventory list-org-accounts --format csv --output accounts.csv

# Legacy form (fully supported)
runbooks inventory list-org-accounts --export-format markdown --output accounts.md
```

#### Supported Commands (13 Total)

| Module | Command | Formats | v1.1.10 |
|--------|---------|---------|---------|
| Inventory | `draw-org` | graphviz, mermaid, diagrams | ✅ |
| Inventory | `list-org-accounts` | json, csv, markdown, table | ✅ |
| Inventory | `list-org-users` | json, csv, markdown, table | ✅ |
| Inventory | `find-lz-versions` | json, csv, markdown, table | ✅ |
| Inventory | `check-landingzone` | json, markdown, table | ✅ |
| Inventory | `check-controltower` | json, markdown, table | ✅ |
| FinOps | `infrastructure analyze` | json, csv, markdown | ✅ |
| FinOps | `elastic-ip` | json, csv, markdown | ✅ |
| FinOps | `ebs` | json, csv, markdown | ✅ |
| FinOps | `vpc-endpoint` | json, csv, markdown | ✅ |
| FinOps | `nat-gateway` | json, csv, markdown | ✅ |
| FinOps | `load-balancer` | json, csv, markdown | ✅ |

#### Migration Guide

**Zero Breaking Changes**: All existing scripts continue working without modification

**Adoption Path**:
- ✅ **Now**: All parameter forms work (choose preferred style)
- 💡 **Recommended**: Adopt `-f` for interactive CLI usage (faster typing)
- 📝 **Scripts**: Update at your convenience (no urgency)
- 🔄 **Future**: v1.2.0 will show deprecation warnings for legacy parameters

## 🏗️ Architecture Highlights

### Modern Stack
- **🐍 Python 3.11+**: Modern async capabilities
- **⚡ UV + Ruff**: 10x faster dependency resolution & linting
- **🎨 Rich CLI**: Beautiful terminal interfaces
- **📊 Pydantic V2**: Type-safe data models
- **🔗 boto3**: Native AWS SDK integration
- **🤖 MCP Servers**: Real-time AWS API access ([MCP Specification](https://modelcontextprotocol.io/))

### Enterprise Features
- **🔐 Multi-Profile AWS**: Seamless account switching
- **🌐 Multi-Language Reports**: EN/JP/KR/VN support
- **📈 DORA Metrics**: DevOps performance tracking
- **🚨 Safety Controls**: Dry-run defaults, approval workflows
- **📊 Executive Dashboards**: Business-ready reporting

## 📚 Documentation

### Quick Links
- **🏠 [Homepage](https://cloudops.oceansoft.io)** - Official project website
- **📖 [Documentation](https://cloudops.oceansoft.io/runbooks/)** - Complete guides
- **🐛 [Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)** - Bug reports & features
- **💬 [Discussions](https://github.com/1xOps/CloudOps-Runbooks/discussions)** - Community support

### Enterprise Module Documentation

| Module | Documentation Hub | Key Business Value | Technical Implementation |
|--------|-------------------|-------------------|--------------------------|
| 💰 **FinOps** | [📊 Module Hub](docs/modules/finops/) | 20-40% cost optimization | [Code](src/runbooks/finops/) |
| 🔒 **Security** | [🛡️ Module Hub](docs/modules/security/) | 15+ security checks, 4 languages | [Code](src/runbooks/security/) |
| 📊 **Inventory** | [🔍 Module Hub](docs/modules/inventory/) | 50+ AWS services discovery | [Code](src/runbooks/inventory/) |
| ⚙️ **Operations** | [🔧 Module Hub](docs/modules/operate/) | Resource lifecycle management | [Code](src/runbooks/operate/) |

## 🔧 Configuration

### AWS Profiles Setup
```bash
# Environment variables for enterprise setup
export AWS_BILLING_PROFILE="your-billing-readonly-profile"
export AWS_MANAGEMENT_PROFILE="your-management-readonly-profile"
export AWS_OPERATIONS_PROFILE="your-operations-readonly-profile"

# Universal profile usage patterns
runbooks finops --profile $AWS_BILLING_PROFILE      # Cost analysis
runbooks inventory collect --profile $AWS_MANAGEMENT_PROFILE  # Discovery
runbooks operate --profile $AWS_OPERATIONS_PROFILE   # Operations
```

### Advanced Configuration
```bash
# Custom configuration directory
export RUNBOOKS_CONFIG_DIR="/path/to/config"

# Performance tuning
export RUNBOOKS_PARALLEL_WORKERS=10
export RUNBOOKS_TIMEOUT=300
```

## 🛡️ Security & Compliance

| Framework | Status | Coverage |
|-----------|--------|----------|
| **AWS Well-Architected** | ✅ Full | 5 pillars |
| **SOC2** | ✅ Compliant | Type II ready |
| **PCI-DSS** | ✅ Validated | Level 1 |
| **HIPAA** | ✅ Ready | Healthcare compliant |
| **ISO 27001** | ✅ Aligned | Security management |

## 🚦 Roadmap

| Version | Timeline | Key Features |
|---------|----------|--------------|
| **v1.1.4** | **Current** | ✅ **Enterprise Production** - ProfileManager + Enhanced exports |
| **v1.2** | Q1 2026 | Enhanced enterprise features and expanded service coverage |
| **v1.3** | Q2 2026 | Enhanced AI orchestration with universal compatibility |
| **v1.5** | Q3 2026 | Self-healing infrastructure across any AWS setup |
| **v2.0** | Q4 2026 | Multi-cloud support (Azure, GCP) |

## 🆘 Support Options

### Community Support (Free)
- 🐛 **[GitHub Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)** - Bug reports & feature requests
- 💬 **[GitHub Discussions](https://github.com/1xOps/CloudOps-Runbooks/discussions)** - Community Q&A

### Enterprise Support
- 🏢 **Professional Services** - Custom deployment assistance
- 🎓 **Training Programs** - Team enablement workshops
- 🛠️ **Custom Development** - Tailored collector modules
- 📧 **Email**: [info@oceansoft.io](mailto:info@oceansoft.io)

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

---

**🏗️ Built with ❤️ by the xOps team at OceanSoft**

*Transform your AWS operations from reactive to proactive with enterprise-grade automation* 🚀