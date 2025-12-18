#!/bin/bash
# Enhanced Potato Policy v2.0 - Violation Reporter
# Framework: Pain → Protocol → Protection
# Author: Mr. Potato 🥔

set -euo pipefail

# Script configuration
SCRIPT_NAME="potato_violation_reporter.sh"
VERSION="2.0"
LOG_FILE="logs/potato_violations.log"
ISSUE_TEMPLATE_FILE="docs/potato-violation-template.md"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# GitHub API configuration
GITHUB_API_URL="https://api.github.com"
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-}"
REPO_NAME="${GITHUB_REPOSITORY#*/}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Issue configuration
ISSUE_LABELS='"security", "potato-policy", "violation", "urgent"'
ISSUE_ASSIGNEES='"'"${REPO_OWNER:-}"'"'

# Logging functions
log_info() {
    local message="$1"
    echo -e "${BLUE}[INFO]${NC} $message" | tee -a "$LOG_FILE"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[WARNING]${NC} $message" | tee -a "$LOG_FILE"
}

log_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE"
}

log_success() {
    local message="$1"
    echo -e "${GREEN}[SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
}

log_violation() {
    local message="$1"
    echo -e "${PURPLE}[VIOLATION_DETECTED]${NC} $message" | tee -a "$LOG_FILE"
}

# Initialize logging
init_logging() {
    mkdir -p logs
    if [[ ! -f "$LOG_FILE" ]]; then
        echo "=== Enhanced Potato Policy Violation Log ===" > "$LOG_FILE"
        echo "Framework: Pain → Protocol → Protection" >> "$LOG_FILE"
        echo "===========================================" >> "$LOG_FILE"
    fi
    log_info "Potato Violation Reporter v$VERSION initialized"
}

# Check for existing violations
check_violations() {
    log_info "Checking for Enhanced Potato Policy violations..."

    local violation_count=0
    local violations_found=()

    # Check if the main security check has been run recently
    local latest_check_log
    latest_check_log=$(find logs -name "enhanced_potato_check_*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "")

    if [[ -n "$latest_check_log" && -f "$latest_check_log" ]]; then
        log_info "Analyzing latest security check: $latest_check_log"

        # Extract violations from the latest check
        while IFS= read -r line; do
            if [[ "$line" == *"[VIOLATION]"* ]]; then
                violations_found+=("$line")
                ((violation_count++))
            fi
        done < "$latest_check_log"

        # Also check for errors that might indicate violations
        while IFS= read -r line; do
            if [[ "$line" == *"[ERROR]"* && "$line" == *"CRITICAL"* ]]; then
                violations_found+=("$line")
                ((violation_count++))
            fi
        done < "$latest_check_log"
    else
        log_warning "No recent security check found - running quick check"
        # Run a quick check if no recent log exists
        if ! bash scripts/enhanced_potato_check.sh >/dev/null 2>&1; then
            log_violation "Quick security check failed - violations likely present"
            violations_found+=("Quick security check failed - detailed scan required")
            violation_count=1
        fi
    fi

    if [ $violation_count -gt 0 ]; then
        log_warning "Found $violation_count Enhanced Potato Policy violations"
        return 1
    else
        log_success "No violations detected"
        return 0
    fi
}

# Generate violation report
generate_violation_report() {
    local violations=("$@")

    log_info "Generating violation report..."

    local report_file="reports/violation-report-$(date +%Y%m%d_%H%M%S).md"
    mkdir -p reports

    cat > "$report_file" << EOF
# 🥔 Enhanced Potato Policy Violation Report

**Framework**: Pain → Protocol → Protection
**Version**: v$VERSION
**Timestamp**: $(date -Iseconds)
**Repository**: ${GITHUB_REPOSITORY:-"Unknown"}
**Branch**: ${GITHUB_REF_NAME:-"Unknown"}
**Workflow**: ${GITHUB_WORKFLOW:-"Manual"}

## 🚨 Security Alert

The Enhanced Potato Policy has detected **${#violations[@]} violation(s)** that require immediate attention.

## 📋 Violation Details

EOF

    local counter=1
    for violation in "${violations[@]}"; do
        echo "### Violation #$counter" >> "$report_file"
        echo '```' >> "$report_file"
        echo "$violation" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
        ((counter++))
    done

    cat >> "$report_file" << EOF

## 🔧 Immediate Actions Required

1. **Review Violations**: Examine each violation listed above
2. **Fix Security Issues**: Address sensitive files, secrets, or policy violations
3. **Update .gitignore**: Ensure all sensitive files are properly ignored
4. **Re-run Audit**: Execute \`make security\` or \`scripts/enhanced_potato_check.sh\`
5. **Verify Compliance**: Ensure all checks pass before closing this issue

## 📚 Resources

- [Enhanced Potato Policy Documentation](docs/enhanced-potato-policy.md)
- [Security Policy](SECURITY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🥔 Potato Policy Enforcement

This issue was automatically created by the Enhanced Potato Policy v$VERSION framework.
**Framework**: Pain → Protocol → Protection

- **Pain**: Violations detected and reported
- **Protocol**: Automated issue creation and tracking
- **Protection**: Systematic security enforcement

## ⚡ Auto-Generated Issue

- **Created**: $(date -Iseconds)
- **Trigger**: Enhanced Potato Policy violation detection
- **Assignee**: Repository maintainer
- **Labels**: security, potato-policy, violation, urgent
- **Priority**: HIGH

---

*This issue will be automatically closed when all violations are resolved and the Enhanced Potato Policy audit passes.*
EOF

    echo "$report_file"
}

# Create GitHub issue
create_github_issue() {
    local report_file="$1"

    if [[ -z "$GITHUB_TOKEN" ]]; then
        log_warning "No GitHub token available - cannot create issue"
        log_info "Violation report available at: $report_file"
        return 1
    fi

    if [[ -z "$REPO_OWNER" || -z "$REPO_NAME" ]]; then
        log_warning "Repository information not available - cannot create issue"
        log_info "Violation report available at: $report_file"
        return 1
    fi

    log_info "Creating GitHub issue for Enhanced Potato Policy violations..."

    local issue_title="🥔 Enhanced Potato Policy Violations Detected - $(date +%Y-%m-%d)"
    local issue_body
    issue_body=$(cat "$report_file")

    # Escape the issue body for JSON
    issue_body=$(echo "$issue_body" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

    # Create the issue using GitHub API
    local response
    response=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$GITHUB_API_URL/repos/$REPO_OWNER/$REPO_NAME/issues" \
        -d "{
            \"title\": \"$issue_title\",
            \"body\": \"$issue_body\",
            \"labels\": [$ISSUE_LABELS],
            \"assignees\": [$ISSUE_ASSIGNEES]
        }" 2>/dev/null || echo '{"message": "API call failed"}')

    # Check if issue was created successfully
    local issue_number
    issue_number=$(echo "$response" | grep -o '"number":[0-9]*' | cut -d':' -f2 || echo "")

    if [[ -n "$issue_number" ]]; then
        local issue_url="https://github.com/$REPO_OWNER/$REPO_NAME/issues/$issue_number"
        log_success "✓ GitHub issue created: #$issue_number"
        log_success "✓ Issue URL: $issue_url"

        # Log the issue creation
        echo "ISSUE_CREATED: $issue_number at $(date -Iseconds)" >> "$LOG_FILE"

        return 0
    else
        log_error "Failed to create GitHub issue"
        log_error "API response: $response"
        return 1
    fi
}

# Check for existing open issues
check_existing_issues() {
    if [[ -z "$GITHUB_TOKEN" || -z "$REPO_OWNER" || -z "$REPO_NAME" ]]; then
        return 1
    fi

    log_info "Checking for existing Enhanced Potato Policy issues..."

    local response
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$GITHUB_API_URL/repos/$REPO_OWNER/$REPO_NAME/issues?labels=potato-policy,violation&state=open" \
        2>/dev/null || echo '[]')

    local issue_count
    issue_count=$(echo "$response" | grep -o '"number":[0-9]*' | wc -l || echo "0")

    if [ "$issue_count" -gt 0 ]; then
        log_warning "Found $issue_count existing Enhanced Potato Policy violation issue(s)"
        return 0
    else
        log_info "No existing violation issues found"
        return 1
    fi
}

# Main execution function
main() {
    init_logging

    log_info "Enhanced Potato Policy Violation Reporter v$VERSION"
    echo -e "${CYAN}Framework: Pain → Protocol → Protection${NC}"
    echo ""

    # Check for violations
    if check_violations; then
        log_success "🥔 No Enhanced Potato Policy violations detected"
        echo "All systems compliant with Enhanced Potato Policy v$VERSION"
        return 0
    fi

    # Get violation details from the latest check
    local violations=()
    local latest_check_log
    latest_check_log=$(find logs -name "enhanced_potato_check_*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "")

    if [[ -n "$latest_check_log" && -f "$latest_check_log" ]]; then
        while IFS= read -r line; do
            if [[ "$line" == *"[VIOLATION]"* || ( "$line" == *"[ERROR]"* && "$line" == *"CRITICAL"* ) ]]; then
                violations+=("$line")
            fi
        done < "$latest_check_log"
    else
        violations+=("Security check failed or no recent audit available")
    fi

    if [ ${#violations[@]} -eq 0 ]; then
        violations+=("Unknown violation detected - manual investigation required")
    fi

    # Generate violation report
    local report_file
    report_file=$(generate_violation_report "${violations[@]}")

    log_info "Violation report generated: $report_file"

    # Check for existing issues to avoid duplicates
    if check_existing_issues; then
        log_warning "Existing violation issues found - not creating duplicate"
        log_info "Violation report available at: $report_file"
        return 1
    fi

    # Create GitHub issue
    if create_github_issue "$report_file"; then
        log_success "🥔 Enhanced Potato Policy violation reported successfully"
        return 1  # Return 1 to indicate violations were found and reported
    else
        log_error "Failed to create GitHub issue for violations"
        log_info "Violation report available at: $report_file"
        return 1
    fi
}

# Execute main function
main "$@"
