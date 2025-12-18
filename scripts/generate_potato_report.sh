#!/bin/bash
# Enhanced Potato Policy v2.0 - Audit Report Generator
# Framework: Pain → Protocol → Protection
# Author: Mr. Potato 🥔

set -euo pipefail

# Script configuration
SCRIPT_NAME="generate_potato_report.sh"
VERSION="2.0"
COMPREHENSIVE_MODE="${1:-false}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Report configuration
TIMESTAMP=$(date -Iseconds)
DATE_SUFFIX=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="reports/enhanced-potato-policy-audit-${DATE_SUFFIX}.md"
LATEST_REPORT="reports/potato-policy-latest.md"
METRICS_FILE="reports/security-metrics.json"

# Logging functions
log_info() {
    local message="$1"
    echo -e "${BLUE}[INFO]${NC} $message"
}

log_success() {
    local message="$1"
    echo -e "${GREEN}[SUCCESS]${NC} $message"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[WARNING]${NC} $message"
}

# Initialize report generation
init_report() {
    mkdir -p reports
    log_info "Enhanced Potato Policy Audit Report Generator v$VERSION"
    echo -e "${CYAN}Framework: Pain → Protocol → Protection${NC}"
}

# Collect system information
collect_system_info() {
    local git_branch
    git_branch=$(git branch --show-current 2>/dev/null || echo "unknown")

    local git_commit
    git_commit=$(git rev-parse HEAD 2>/dev/null | cut -c1-8 || echo "unknown")

    local total_files
    total_files=$(find . -type f -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" | wc -l)

    local python_version
    python_version=$(python --version 2>&1 | cut -d' ' -f2 || echo "not available")

    echo "SYSTEM_INFO|Branch:$git_branch|Commit:$git_commit|Files:$total_files|Python:$python_version"
}

# Analyze security check results
analyze_security_results() {
    local latest_check_log
    latest_check_log=$(find logs -name "enhanced_potato_check_*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "")

    local violation_count=0
    local warning_count=0
    local success_count=0
    local violations=()
    local warnings=()
    local successes=()

    if [[ -n "$latest_check_log" && -f "$latest_check_log" ]]; then
        while IFS= read -r line; do
            if [[ "$line" == *"[VIOLATION]"* ]]; then
                violations+=("$line")
                ((violation_count++))
            elif [[ "$line" == *"[WARNING]"* ]]; then
                warnings+=("$line")
                ((warning_count++))
            elif [[ "$line" == *"[SUCCESS]"* ]]; then
                successes+=("$line")
                ((success_count++))
            fi
        done < "$latest_check_log"

        echo "SECURITY_RESULTS|Log:$latest_check_log|Violations:$violation_count|Warnings:$warning_count|Successes:$success_count"
    else
        echo "SECURITY_RESULTS|Log:none|Violations:unknown|Warnings:unknown|Successes:unknown"
    fi

    # Export arrays for use in report generation
    printf '%s\n' "${violations[@]}" > /tmp/violations.txt 2>/dev/null || touch /tmp/violations.txt
    printf '%s\n' "${warnings[@]}" > /tmp/warnings.txt 2>/dev/null || touch /tmp/warnings.txt
    printf '%s\n' "${successes[@]}" > /tmp/successes.txt 2>/dev/null || touch /tmp/successes.txt
}

# Collect file statistics
collect_file_stats() {
    local python_files
    python_files=$(find . -name "*.py" -not -path "./.git/*" -not -path "./.venv/*" | wc -l)

    local script_files
    script_files=$(find . -name "*.sh" -not -path "./.git/*" -not -path "./.venv/*" | wc -l)

    local config_files
    config_files=$(find . \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.toml" \) -not -path "./.git/*" -not -path "./.venv/*" | wc -l)

    local sensitive_files
    sensitive_files=$(find . -type f \( -name "*.env" -o -name "*.pem" -o -name "*.key" -o -name "secrets.*" \) -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null | wc -l || echo "0")

    echo "FILE_STATS|Python:$python_files|Scripts:$script_files|Config:$config_files|Sensitive:$sensitive_files"
}

# Check ignore file coverage
check_ignore_coverage() {
    local gitignore_patterns=0
    local dockerignore_patterns=0
    local codespell_patterns=0

    if [[ -f ".gitignore" ]]; then
        gitignore_patterns=$(wc -l < .gitignore 2>/dev/null || echo "0")
    fi

    if [[ -f ".dockerignore" ]]; then
        dockerignore_patterns=$(wc -l < .dockerignore 2>/dev/null || echo "0")
    fi

    if [[ -f ".codespell-ignore" ]]; then
        codespell_patterns=$(wc -l < .codespell-ignore 2>/dev/null || echo "0")
    fi

    echo "IGNORE_COVERAGE|GitIgnore:$gitignore_patterns|DockerIgnore:$dockerignore_patterns|CodespellIgnore:$codespell_patterns"
}

# Generate comprehensive report
generate_report() {
    log_info "Generating comprehensive Enhanced Potato Policy audit report..."

    # Collect all data
    local system_info
    system_info=$(collect_system_info)

    local security_results
    security_results=$(analyze_security_results)

    local file_stats
    file_stats=$(collect_file_stats)

    local ignore_coverage
    ignore_coverage=$(check_ignore_coverage)

    # Parse collected data
    local git_branch
    git_branch=$(echo "$system_info" | cut -d'|' -f2 | cut -d':' -f2)

    local git_commit
    git_commit=$(echo "$system_info" | cut -d'|' -f3 | cut -d':' -f2)

    local total_files
    total_files=$(echo "$system_info" | cut -d'|' -f4 | cut -d':' -f2)

    local python_version
    python_version=$(echo "$system_info" | cut -d'|' -f5 | cut -d':' -f2)

    local violation_count
    violation_count=$(echo "$security_results" | cut -d'|' -f3 | cut -d':' -f2)

    local warning_count
    warning_count=$(echo "$security_results" | cut -d'|' -f4 | cut -d':' -f2)

    local success_count
    success_count=$(echo "$security_results" | cut -d'|' -f5 | cut -d':' -f2)

    # Determine compliance status
    local compliance_status="✅ COMPLIANT"
    local compliance_color="🟢"
    if [[ "$violation_count" != "0" && "$violation_count" != "unknown" ]]; then
        compliance_status="❌ VIOLATIONS DETECTED"
        compliance_color="🔴"
    elif [[ "$warning_count" != "0" && "$warning_count" != "unknown" ]]; then
        compliance_status="⚠️ WARNINGS PRESENT"
        compliance_color="🟡"
    fi

    # Generate the main report
    cat > "$REPORT_FILE" << EOF
# 🥔 Enhanced Potato Policy Audit Report

**Framework**: Pain → Protocol → Protection
**Version**: v$VERSION
**Generated**: $TIMESTAMP
**Repository**: ${GITHUB_REPOSITORY:-$(basename "$(pwd)")}
**Comprehensive Mode**: $COMPREHENSIVE_MODE

---

## 📊 Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Compliance Status** | $compliance_status | $compliance_color |
| **Security Violations** | $violation_count | $([ "$violation_count" = "0" ] && echo "✅" || echo "❌") |
| **Warnings** | $warning_count | $([ "$warning_count" = "0" ] && echo "✅" || echo "⚠️") |
| **Successful Checks** | $success_count | ✅ |
| **Framework Version** | Enhanced Potato Policy v$VERSION | ✅ |

---

## 🔍 System Information

| Component | Details |
|-----------|---------|
| **Git Branch** | \`$git_branch\` |
| **Git Commit** | \`$git_commit\` |
| **Total Files** | $total_files |
| **Python Version** | $python_version |
| **Virtual Environment** | \`${VIRTUAL_ENV:-"Not detected"}\` |
| **Audit Timestamp** | $TIMESTAMP |

---

## 📁 File Analysis

EOF

    # Add file statistics
    local python_files
    python_files=$(echo "$file_stats" | cut -d'|' -f2 | cut -d':' -f2)

    local script_files
    script_files=$(echo "$file_stats" | cut -d'|' -f3 | cut -d':' -f2)

    local config_files
    config_files=$(echo "$file_stats" | cut -d'|' -f4 | cut -d':' -f2)

    local sensitive_files
    sensitive_files=$(echo "$file_stats" | cut -d'|' -f5 | cut -d':' -f2)

    cat >> "$REPORT_FILE" << EOF
| File Type | Count | Security Impact |
|-----------|-------|-----------------|
| **Python Files** | $python_files | Medium - Code execution |
| **Script Files** | $script_files | High - System execution |
| **Configuration Files** | $config_files | Medium - Settings exposure |
| **Sensitive Files** | $sensitive_files | $([ "$sensitive_files" = "0" ] && echo "✅ None" || echo "🚨 Critical") |

---

## 🛡️ Security Protection Coverage

EOF

    # Add ignore file coverage
    local gitignore_patterns
    gitignore_patterns=$(echo "$ignore_coverage" | cut -d'|' -f2 | cut -d':' -f2)

    local dockerignore_patterns
    dockerignore_patterns=$(echo "$ignore_coverage" | cut -d'|' -f3 | cut -d':' -f2)

    local codespell_patterns
    codespell_patterns=$(echo "$ignore_coverage" | cut -d'|' -f4 | cut -d':' -f2)

    cat >> "$REPORT_FILE" << EOF
| Protection Layer | Patterns | Status |
|------------------|----------|--------|
| **Git Ignore** | $gitignore_patterns | $([ "$gitignore_patterns" -gt "0" ] && echo "✅ Active" || echo "⚠️ Missing") |
| **Docker Ignore** | $dockerignore_patterns | $([ "$dockerignore_patterns" -gt "0" ] && echo "✅ Active" || echo "⚠️ Missing") |
| **Codespell Ignore** | $codespell_patterns | $([ "$codespell_patterns" -gt "0" ] && echo "✅ Active" || echo "⚠️ Missing") |

---

EOF

    # Add detailed results if violations or warnings exist
    if [[ -f "/tmp/violations.txt" && -s "/tmp/violations.txt" ]]; then
        cat >> "$REPORT_FILE" << EOF
## 🚨 Security Violations

EOF
        local counter=1
        while IFS= read -r violation; do
            if [[ -n "$violation" ]]; then
                echo "### Violation #$counter" >> "$REPORT_FILE"
                echo '```' >> "$REPORT_FILE"
                echo "$violation" >> "$REPORT_FILE"
                echo '```' >> "$REPORT_FILE"
                echo "" >> "$REPORT_FILE"
                ((counter++))
            fi
        done < /tmp/violations.txt

        cat >> "$REPORT_FILE" << EOF

---

EOF
    fi

    if [[ -f "/tmp/warnings.txt" && -s "/tmp/warnings.txt" ]]; then
        cat >> "$REPORT_FILE" << EOF
## ⚠️ Security Warnings

EOF
        local counter=1
        while IFS= read -r warning; do
            if [[ -n "$warning" ]]; then
                echo "### Warning #$counter" >> "$REPORT_FILE"
                echo '```' >> "$REPORT_FILE"
                echo "$warning" >> "$REPORT_FILE"
                echo '```' >> "$REPORT_FILE"
                echo "" >> "$REPORT_FILE"
                ((counter++))
            fi
        done < /tmp/warnings.txt

        cat >> "$REPORT_FILE" << EOF

---

EOF
    fi

    # Add successful checks summary
    cat >> "$REPORT_FILE" << EOF
## ✅ Successful Security Checks

EOF

    if [[ -f "/tmp/successes.txt" && -s "/tmp/successes.txt" ]]; then
        while IFS= read -r success; do
            if [[ -n "$success" ]]; then
                echo "- $success" >> "$REPORT_FILE"
            fi
        done < /tmp/successes.txt
    else
        echo "- No successful checks recorded" >> "$REPORT_FILE"
    fi

    # Add framework information and next steps
    cat >> "$REPORT_FILE" << EOF

---

## 🥔 Enhanced Potato Policy Framework

### Framework Philosophy: Pain → Protocol → Protection

1. **Pain**: Identify and surface security vulnerabilities
2. **Protocol**: Systematic detection and reporting processes
3. **Protection**: Automated enforcement and compliance monitoring

### Audit Components

- **🔍 Sensitive File Detection**: Scans for credentials, keys, certificates
- **🛡️ Code Security Analysis**: Identifies dangerous patterns and practices
- **📁 File Permission Validation**: Ensures proper access controls
- **🔄 Git History Scanning**: Checks for leaked secrets in commits
- **🚧 Ignore File Validation**: Verifies protection coverage

### Compliance Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **✅ Compliant** | All checks passed | Continue monitoring |
| **⚠️ Warnings** | Minor issues detected | Address recommendations |
| **❌ Violations** | Critical issues found | **Immediate action required** |

---

## 🚀 Next Steps

EOF

    if [[ "$violation_count" != "0" && "$violation_count" != "unknown" ]]; then
        cat >> "$REPORT_FILE" << EOF
### 🔥 Critical Actions Required

1. **🚨 Address Violations**: Review and fix all security violations immediately
2. **🔧 Update Protection**: Ensure sensitive files are in .gitignore
3. **🧹 Clean History**: Remove any secrets from git history if necessary
4. **✅ Re-audit**: Run \`scripts/enhanced_potato_check.sh\` to verify fixes

EOF
    elif [[ "$warning_count" != "0" && "$warning_count" != "unknown" ]]; then
        cat >> "$REPORT_FILE" << EOF
### ⚠️ Recommended Actions

1. **📋 Review Warnings**: Address security recommendations
2. **🛡️ Enhance Protection**: Consider additional security measures
3. **📊 Monitor Progress**: Track improvement over time

EOF
    else
        cat >> "$REPORT_FILE" << EOF
### 🎉 Maintenance Actions

1. **📅 Schedule Regular Audits**: Maintain compliance with periodic checks
2. **📈 Monitor Metrics**: Track security posture improvements
3. **🔄 Update Framework**: Keep Enhanced Potato Policy current

EOF
    fi

    cat >> "$REPORT_FILE" << EOF

---

## 📚 Resources

- **[Enhanced Potato Policy Documentation](docs/enhanced-potato-policy.md)**
- **[Security Policy](SECURITY.md)**
- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Function Contracts](FUNCTION_CONTRACTS.md)**

---

## 📋 Report Metadata

- **Report File**: \`$REPORT_FILE\`
- **Latest Symlink**: \`$LATEST_REPORT\`
- **Metrics File**: \`$METRICS_FILE\`
- **Framework Version**: Enhanced Potato Policy v$VERSION
- **Generation Mode**: $([ "$COMPREHENSIVE_MODE" = "true" ] && echo "Comprehensive" || echo "Standard")
- **Execution Context**: ${GITHUB_WORKFLOW:-"Local execution"}

---

*🥔 Enhanced Potato Policy v$VERSION - Framework: Pain → Protocol → Protection*
*Auto-generated report: $TIMESTAMP*
EOF

    # Create symlink to latest report
    ln -sf "$(basename "$REPORT_FILE")" "$LATEST_REPORT"

    # Clean up temporary files
    rm -f /tmp/violations.txt /tmp/warnings.txt /tmp/successes.txt 2>/dev/null || true

    log_success "✓ Report generated: $REPORT_FILE"
    log_success "✓ Latest report symlink: $LATEST_REPORT"
}

# Main execution
main() {
    init_report

    log_info "Comprehensive mode: $COMPREHENSIVE_MODE"

    generate_report

    log_success "🥔 Enhanced Potato Policy audit report generation complete"
    echo ""
    echo "Report files:"
    echo "  - Main report: $REPORT_FILE"
    echo "  - Latest symlink: $LATEST_REPORT"

    if [[ -f "$METRICS_FILE" ]]; then
        echo "  - Metrics: $METRICS_FILE"
    fi
}

# Execute main function
main "$@"
