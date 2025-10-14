<h1 align="center">
  <a href="">
    <picture>
      <source height="220" media="(prefers-color-scheme: dark)" srcset="https://i.imgur.com/nGEReZh.png">
      <img height="200" alt="Argus" src="https://i.imgur.com/FL0dmHd.png">
    </picture>
  </a>
  <br>
</h1>
<p align="center">
   A Python-based toolkit for Information Gathering & Reconnaissance
</p>

![screenshot](https://i.imgur.com/HIQWPPO.gif)
---

## About The Project

Argus is an all-in-one, Python-powered toolkit designed to streamline the process of information gathering and reconnaissance. With a user-friendly interface and a suite of powerful modules, Argus empowers you to explore networks, web applications, and security configurations efficiently and effectively.

Whether you're conducting research, performing security assessments with proper authorization, or just curious about network infrastructures, Argus brings a wealth of information to your fingertips—all in one place.

## ⚠️ WARNING: LEGAL DISCLAIMER

This tool is intended for **educational and ethical use only**. The author is not liable for any illegal use or misuse of this tool. Users are solely responsible for their actions and must ensure they have explicit permission to scan the target systems.

---

## 👀 Screenshots

Take a look at Argus in action:
<p float="left" align="middle">
  <img src="https://i.imgur.com/uUjTbCb.png" width="49%">
  <img src="https://i.imgur.com/iPqLYX6.png" width="49%">
</p>
<p float="left" align="middle">
  <img src="https://i.imgur.com/SwcLyfU.png" width="49%">
  <img src="https://i.imgur.com/bfxcx88.png" width="49%">
</p>
<p float="left" align="middle">
  <img src="https://i.imgur.com/SgPJjH7.png" width="49%">
  <img src="https://i.imgur.com/y4N4vEX.png" width="49%">
</p>
<p float="left" align="middle">
  <img src="https://i.imgur.com/gP1XFkf.png" width="49%">
  <img src="https://i.imgur.com/PL89DjC.png" width="49%">
</p>

---

## ⚙️ Installation

### Quick Start

#### Option 1: No Installation (Run Directly)
```bash
git clone https://github.com/jasonxtn/argus.git
cd argus
python -m argus
```

#### Option 2: Using pip (Recommended)
```bash
pip install argus-recon
argus
```

#### Option 3: Full Installation
```bash
git clone https://github.com/jasonxtn/argus.git
cd argus
chmod +x install.sh && ./install.sh
python -m argus
```

#### Option 4: Docker
```bash
git clone https://github.com/jasonxtn/argus.git
cd argus
docker build -t argus-recon:latest .
docker run -it --rm -v $(pwd)/results:/app/results argus-recon:latest
```

---

## 📖 Usage

### Getting Started

1. **Launch Argus**:
   ```bash
   argus
   # or if running from folder: python -m argus
   ```

2. **Browse available modules**:
   ```
   argus> modules
   ```

3. **Select a module**:
   ```
   argus> use 1
   ```

4. **Set target and options**:
   ```
   argus> set target example.com
   argus> set threads 10
   ```

5. **Run the module**:
   ```
   argus> run
   ```

### Commands Cheatsheet

| Command | Category | Description | Example |
|---------|----------|-------------|---------|
| `modules` | Discovery | List all modules | `modules` |
| `modules -d` | Discovery | List with details | `modules -d` |
| `search` | Discovery | Search by keyword | `search ssl` |
| `use` | Selection | Select module | `use 42` |
| `helpmod` | Help | Module help | `helpmod 42` |
| `set target` | Config | Set target | `set target example.com` |
| `set` | Config | Set options | `set threads 20` |
| `unset` | Config | Unset options | `unset target` |
| `opts` | Config | Show options | `opts` |
| `scope` | Config | Show config | `scope` |
| `profile` | Config | Apply profile | `profile speed` |
| `run` | Execute | Run selected | `run` |
| `runall` | Execute | Run category | `runall infra` |
| `runfav` | Execute | Run favorites | `runfav` |
| `last` | Execute | Re-run last | `last` |
| `fav` | Favorites | Manage favorites | `fav add 42` |
| `show modules` | Info | Browse modules | `show modules` |
| `show api_status` | Info | Check APIs | `show api_status` |
| `show options` | Info | Show options | `show options` |
| `show options_full` | Info | Detailed options | `show options_full` |
| `info` | Info | Project info | `info` |
| `recent` | Info | Recent modules | `recent` |
| `viewout` | Output | View cached output | `viewout` |
| `grepout` | Output | Search output | `grepout "192.168"` |
| `clear` | Utility | Clear screen | `clear` |
| `banner` | Utility | Show banner | `banner` |
| `reset` | Utility | Reset config | `reset` |
| `exit` | Utility | Exit Argus | `exit` |
| `quit` | Utility | Exit Argus | `quit` |
| `help` | Help | Show help | `help` |

#### 🔄 **Command Aliases**
| Alias | Full Command | Description |
|-------|--------------|-------------|
| `hm` | `helpmod` | Module help |

#### 🎯 **Quick Reference**
```bash
# Basic workflow
modules          # Browse available modules
use 42           # Select module 42
set target example.com
run              # Execute module

# Search and filter
search ssl       # Find SSL-related modules
modules tag:dns  # Filter by capability tag

# Batch operations
runall infra     # Run all infrastructure modules
runfav           # Run favorite modules

# Information
show modules     # Detailed module list
helpmod 42       # Module-specific help
scope            # Current configuration
show api_status  # Check API configuration
```

### Example Session

```bash
$ argus

argus> modules
argus> use 1
argus> set target example.com
argus> set threads 10
argus> run

argus> modules -d
argus> use 65
argus> set max_pages 200
argus> run

argus> show api_status
argus> fav add 1
argus> runfav
```

---

## 🛠️ Available Modules

<div align="center">

### **134 Security Reconnaissance Modules**

*Comprehensive toolkit for network, web, and security analysis*

</div>

---

### 📋 **All Modules** *(135 total)*

| Network & Infrastructure | Web Application Analysis | Security & Threat Intelligence |
|--------------------------|---------------------------|--------------------------------|
| 1. Associated Hosts | 53. Archive History | 103. Censys Reconnaissance |
| 2. DNS Over HTTPS | 54. Broken Links Detection | 104. Certificate Authority Recon |
| 3. DNS Records | 55. Carbon Footprint | 105. Data Leak Detection |
| 4. DNSSEC Check | 56. CMS Detection | 106. Exposed Environment Files |
| 5. Domain Info | 57. Cookies Analyzer | 107. Firewall Detection |
| 6. Domain Reputation Check | 58. Content Discovery | 108. Global Ranking |
| 7. HTTP/2 & HTTP/3 Support | 59. Crawler | 109. HTTP Headers |
| 8. IP Info | 60. Robots.txt Analyzer | 110. HTTP Security Features |
| 9. Open Ports Scan | 61. Directory Finder | 111. Malware & Phishing Check |
| 10. Server Info | 62. Email Harvesting | 112. Pastebin Monitoring |
| 11. Server Location | 63. Performance Monitoring | 113. Privacy & GDPR Compliance |
| 12. SSL Chain Analysis | 64. Quality Metrics | 114. Security.txt Check |
| 13. SSL Expiry Alert | 65. Redirect Chain | 115. Shodan Reconnaissance |
| 14. TLS Cipher Suites | 66. Sitemap Parsing | 116. SSL Labs Report |
| 15. TLS Handshake Simulation | 67. Social Media Presence | 117. SSL Pinning Check |
| 16. Traceroute | 68. Technology Stack Detection | 118. Subdomain Enumeration |
| 17. TXT Records | 69. Third-Party Integrations | 119. Subdomain Takeover |
| 18. WHOIS Lookup | 70. JavaScript File Analyzer | 120. VirusTotal Scan |
| 19. Zone Transfer | 71. CORS Misconfiguration Scanner | 121. CT Log Query |
| 20. ASN Lookup | 72. Login Page Brute Identifier | 122. Breached Credentials Lookup |
| 21. Reverse IP Lookup | 73. Hidden Parameter Discovery | 123. Cloud Bucket Exposure |
| 22. IP Range Scanner | 74. Clickjacking Test | 124. JWT Token Analyzer |
| 23. RDAP Lookup | 75. Form Grabber | 125. Exposed API Endpoints |
| 24. NTP Information Leak | 76. Favicon Hashing | 126. Git Repository Exposure Check |
| 25. IPv6 Reachability Test | 77. HTML Comments Extractor | 127. Typosquat Domain Checker |
| 26. BGP Route Analysis | 78. CAPTCHA Presence Checker | 128. SPF / DKIM / DMARC Validator |
| 27. CDN Detection | 79. JavaScript Obfuscation Detector | 129. Open Redirect Finder |
| 28. Reverse DNS Scan | 80. Virtual Host Fuzzer | 130. Rate-Limit & WAF Bypass Test |
| 29. Network Timezone Detection | 81. Session Cookie Lifetime Checker | 131. Security Changelog Diff |
| 30. Geo-DNS Footprint | 82. HTML5 Feature Abuse Detector | 132. Session Hijacking (Passive) |
| 31. SPF Network Extractor | 83. Autocomplete Vulnerability Checker | 133. Rogue Certificate Check |
| 32. NS Geo/ASN Diversity | 84. Embedded Object Hunter | 134. JS Malware Scanner |
| 33. DNS SLA Latency Monitor | 85. Multi-Language URL Tester | 135. Cloud Service Enumeration |
| 34. RPKI Route Validity | 86. Pixel Tracker Finder | |
| 35. Recursive Nameserver Leak | 87. SEO Abuse Detector | |
| 36. Dual-Stack Behavior Profiler | 88. Dependency JS/CDN Scanner | |
| 37. ICMP Reachability Matrix | 89. WebSocket Endpoint Sniffer | |
| 38. IP Allocation History Tracker | 90. API Schema Grabber | |
| 39. Autonomous Neighbor Peering Map | 91. Lazy-Load Resource Finder | |
| 40. TLS Session Resumption Map | 92. HTTP Method Enumerator | |
| 41. Network Certificate Inventory | 93. GraphQL Introspection Probe | |
| 42. SSH Banner & Key Fingerprinter | 94. File Upload Surface Finder | |
| 43. SNMP Public Community Checker | 95. DOM Sink Scanner | |
| 44. SNMP Bulk Walk | 96. Cache Behavior Analyzer | |
| 45. UDP Service Sampler | 97. Cookie Scope Diff Across Subdomains | |
| 46. NetBIOS Name Query | 98. CSP Deep Analyzer | |
| 47. TTL Analysis | 99. Third-Party Script Risk Profiler | |
| 48. IRR Routing Registry Analyzer | 100. Static Asset Fingerprinter | |
| 49. Dual Stack Diff | 101. Crawl Rules | |
| 50. DNS CAA Checker | 102. Email Config | |
| 51. Decoy DNS Beacon | | |
| 52. Geo IP Spoof Detection | | |

---

### 🎯 **Module Usage Tips**

<div align="center">

**Quick Module Discovery**

</div>

```bash
# Browse all modules
modules

# Filter by category
modules infra    # Network & Infrastructure
modules web      # Web Application Analysis  
modules sec      # Security & Threat Intelligence

# Search by capability
search dns       # Find DNS-related modules
search ssl       # Find SSL/TLS modules
search api       # Find API testing modules

# Get detailed help
helpmod 42       # Module-specific help
show modules -d  # Detailed module list
```

<div align="center">

**Popular Module Combinations**

</div>

| Use Case | Recommended Modules |
|----------|-------------------|
| **Quick Recon** | 1, 3, 8, 9, 12 |
| **Web Security** | 20, 25, 26, 43, 44 |
| **SSL/TLS Audit** | 12, 13, 14, 15, 50 |
| **Subdomain Enum** | 3, 52, 53, 55+ |
| **API Security** | 37+, 55+, 55+ |
| **Threat Intel** | 37, 49, 54, 55+ |

---

## ⚡ Performance Profiles

Pre‑configured scan depths and behaviors for different use cases:

| Profile | Use When | Effect |
|---------|----------|--------|
| `speed` | Quick reconnaissance | Small crawl, faster timeout, minimal threads |
| `deep` | Full comprehensive sweep | Large crawl, slower timeout, full cert chain, maximum threads |
| `safe` | Low-impact scanning | Small crawl, conservative timeouts |

**Usage:**
```bash
argus> profile deep
argus> run 1 3 8
```



## 🛠️ Configuration

### API Keys Setup

Enhance functionality by configuring API keys in `config/settings.py` or as environment variables:

```bash
export VIRUSTOTAL_API_KEY="your_key_here"
export SHODAN_API_KEY="your_key_here"
export CENSYS_API_ID="your_id_here"
export CENSYS_API_SECRET="your_secret_here"
export GOOGLE_API_KEY="your_key_here"
export HIBP_API_KEY="your_key_here"
```

**Check API status:**
```bash
argus> show api_status
```

### Configuration Options

Edit `config/settings.py` to customize:
- Default request timeouts and retry logic
- Thread limits and concurrency settings
- Export settings (TXT/CSV output)
- Logging levels and destinations
- User agent strings and headers

---

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install Argus
make install-dev   # Install with development dependencies
make test          # Run tests
make lint          # Run code linting
make format        # Format code with black/isort
make docker-build  # Build Docker image
make security-check # Run security analysis
```

---

## 🔄 Changelog

### Version 2.0 (Current)
**Major refactor: Complete CLI redesign and module expansion**

- **New interactive CLI** - Full command-line interface with 25+ commands
- **135 modules** - Expanded from 50 modules
- **Better UI** - Professional formatting and progress tracking
- **Multi-threading** - Improved performance with concurrent execution
- **API integrations** - Shodan, VirusTotal, Censys, SSL Labs support
- **Export capabilities** - TXT, CSV, JSON output formats
- **Configuration system** - Profiles, settings, and API key management
- **Module discovery** - Search, browse, and favorite modules
- **Batch operations** - Run multiple modules simultaneously

### Version 1.x (Legacy)
**Original simple number-based interface**

- Simple number input system (1-50)
- Basic 50 reconnaissance modules
- Console text output only
- Fixed configuration settings

---

**Note**: Version 2.0 introduces breaking changes. Users must learn new CLI commands instead of the previous number-based system.

---

## ⭐️ Show Your Support

If this tool has been helpful to you, please consider giving us a star on GitHub! Your support means a lot to us and helps others discover the project.

### Issues & Bug Reports

- Check existing issues before reporting
- Provide detailed reproduction steps
- Include system information and error logs

---
