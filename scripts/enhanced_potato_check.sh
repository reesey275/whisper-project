#!/bin/bash
# Enhanced Potato Policy v2.0 - Comprehensive Security Checker
# Framework: Pain → Protocol → Protection
# Author: Mr. Potato 🥔

set -euo pipefail

# Script configuration
SCRIPT_NAME="enhanced_potato_check.sh"
VERSION="2.0"
LOG_FILE="logs/enhanced_potato_check_$(date +%Y%m%d_%H%M%S).log"
VERBOSE=false
VIOLATION_COUNT=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Enhanced Potato Policy patterns
SENSITIVE_PATTERNS=(
    "password\s*=\s*['\"].*['\"]"
    "api_key\s*=\s*['\"].*['\"]"
    "secret\s*=\s*['\"].*['\"]"
    "token\s*=\s*['\"].*['\"]"
    "aws_access_key_id"
    "aws_secret_access_key"
    "openai_api_key"
    "github_token"
    "-----BEGIN RSA PRIVATE KEY-----"
    "-----BEGIN PRIVATE KEY-----"
    "ssh-rsa AAAA"
    "ssh-ed25519 AAAA"
)

POTATO_POLICY_VIOLATIONS=(
    "TODO.*hack"
    "FIXME.*security"
    "XXX.*bypass"
    "eval\s*\("
    "exec\s*\("
    "os\.system\s*\("
    "subprocess\.call.*shell=True"
    "shell=True"
    "pickle\.loads\s*\("
    "yaml\.load\s*\("
)

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
    echo -e "${PURPLE}[VIOLATION]${NC} $message" | tee -a "$LOG_FILE"
    ((VIOLATION_COUNT++))
}

# Initialize logging
init_logging() {
    mkdir -p logs
    echo "=== Enhanced Potato Policy v$VERSION Audit ===" > "$LOG_FILE"
    echo "Timestamp: $(date -Iseconds)" >> "$LOG_FILE"
    echo "Framework: Pain → Protocol → Protection" >> "$LOG_FILE"
    echo "==========================================" >> "$LOG_FILE"
    log_info "Enhanced Potato Policy v$VERSION initialized"
}

# Check for sensitive files
check_sensitive_files() {
    log_info "Checking for sensitive files..."

    local sensitive_files=()

    # Check for common sensitive file patterns
    while IFS= read -r -d '' file; do
        sensitive_files+=("$file")
    done < <(find . -type f \
        \( -name "*.env" -o -name "*.pem" -o -name "*.key" -o -name "secrets.*" \
           -o -name "id_rsa" -o -name "id_ed25519" -o -name "*.p12" \
           -o -name "*.pfx" -o -name "keystore.*" -o -name "*.jks" \) \
        -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" \
        -print0 2>/dev/null || true)

    if [ ${#sensitive_files[@]} -gt 0 ]; then
        log_warning "Found ${#sensitive_files[@]} potentially sensitive files:"
        for file in "${sensitive_files[@]}"; do
            log_violation "Sensitive file detected: $file"

            # Check if file is properly ignored
            if ! git check-ignore "$file" >/dev/null 2>&1; then
                log_error "CRITICAL: Sensitive file '$file' is NOT in .gitignore!"
                ((VIOLATION_COUNT++))
            else
                log_info "✓ File '$file' is properly ignored"
            fi
        done
    else
        log_success "No sensitive files found"
    fi
}

# Check for secrets in code
check_secrets_in_code() {
    log_info "Scanning code for embedded secrets..."

    local files_to_check=()
    while IFS= read -r -d '' file; do
        files_to_check+=("$file")
    done < <(find . -type f \
        \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" \
           -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.md" \) \
        -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" \
        -not -path "./logs/*" -print0 2>/dev/null || true)

    for file in "${files_to_check[@]}"; do
        if [[ "$VERBOSE" == true ]]; then
            log_info "Scanning: $file"
        fi

        # Check for sensitive patterns
        for pattern in "${SENSITIVE_PATTERNS[@]}"; do
            if grep -qiE "$pattern" "$file" 2>/dev/null; then
                log_violation "Potential secret in $file: pattern '$pattern'"

                # Show context if verbose
                if [[ "$VERBOSE" == true ]]; then
                    echo "Context:" | tee -a "$LOG_FILE"
                    grep -nE "$pattern" "$file" | head -3 | tee -a "$LOG_FILE"
                fi
            fi
        done

        # Check for Potato Policy violations
        for violation in "${POTATO_POLICY_VIOLATIONS[@]}"; do
            if grep -qE "$violation" "$file" 2>/dev/null; then
                log_violation "Potato Policy violation in $file: '$violation'"

                if [[ "$VERBOSE" == true ]]; then
                    echo "Context:" | tee -a "$LOG_FILE"
                    grep -nE "$violation" "$file" | head -2 | tee -a "$LOG_FILE"
                fi
            fi
        done
    done
}

# Check git history for secrets
check_git_history() {
    log_info "Checking git history for leaked secrets..."

    # Check recent commits for sensitive patterns
    local recent_commits
    recent_commits=$(git log --oneline -n 10 --format="%H" 2>/dev/null || echo "")

    if [[ -n "$recent_commits" ]]; then
        while IFS= read -r commit; do
            if [[ -n "$commit" ]]; then
                # Check commit diff for sensitive patterns
                local commit_diff
                commit_diff=$(git show "$commit" --format="" 2>/dev/null || echo "")

                for pattern in "${SENSITIVE_PATTERNS[@]}"; do
                    if echo "$commit_diff" | grep -qiE "$pattern" 2>/dev/null; then
                        log_violation "Potential secret in commit $commit: pattern '$pattern'"
                    fi
                done
            fi
        done <<< "$recent_commits"
    else
        log_info "No git history available"
    fi
}

# Check file permissions
check_file_permissions() {
    log_info "Checking file permissions..."

    # Check for overly permissive files
    local permissive_files=()
    while IFS= read -r -d '' file; do
        permissive_files+=("$file")
    done < <(find . -type f -perm /o+w \
        -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" \
        -print0 2>/dev/null || true)

    if [ ${#permissive_files[@]} -gt 0 ]; then
        log_warning "Found ${#permissive_files[@]} world-writable files:"
        for file in "${permissive_files[@]}"; do
            log_violation "World-writable file: $file ($(stat -c '%a' "$file" 2>/dev/null || echo 'unknown'))"
        done
    else
        log_success "No world-writable files found"
    fi

    # Check for executable scripts without proper shebang
    local scripts_without_shebang=()
    while IFS= read -r -d '' file; do
        if [[ -x "$file" ]] && ! head -n1 "$file" | grep -q "^#!" 2>/dev/null; then
            scripts_without_shebang+=("$file")
        fi
    done < <(find . -type f -name "*.sh" -print0 2>/dev/null || true)

    if [ ${#scripts_without_shebang[@]} -gt 0 ]; then
        for script in "${scripts_without_shebang[@]}"; do
            log_violation "Executable script without shebang: $script"
        done
    fi
}

# Check ignore files
check_ignore_files() {
    log_info "Validating ignore files..."

    local ignore_files=(".gitignore" ".dockerignore" ".codespell-ignore")

    for ignore_file in "${ignore_files[@]}"; do
        if [[ -f "$ignore_file" ]]; then
            log_success "✓ $ignore_file exists"

            # Count patterns
            local pattern_count
            pattern_count=$(wc -l < "$ignore_file" 2>/dev/null || echo "0")
            log_info "$ignore_file contains $pattern_count patterns"

            # Check for common security patterns
            local security_patterns=("*.env" "*.key" "*.pem" "secrets.*" "id_rsa" "id_ed25519")
            for pattern in "${security_patterns[@]}"; do
                if ! grep -q "$pattern" "$ignore_file" 2>/dev/null; then
                    log_warning "$ignore_file missing security pattern: $pattern"
                fi
            done
        else
            log_violation "Missing ignore file: $ignore_file"
        fi
    done
}

# Check virtual environment
check_virtual_environment() {
    log_info "Checking virtual environment status..."

    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log_success "✓ Virtual environment active: $VIRTUAL_ENV"

        # Check Python version
        local python_version
        python_version=$(python --version 2>&1 | cut -d' ' -f2)
        log_info "Python version: $python_version"

        # Check for security packages
        local security_packages=("bandit" "safety" "pip-audit")
        for package in "${security_packages[@]}"; do
            if pip list | grep -q "^$package " 2>/dev/null; then
                log_success "✓ Security package installed: $package"
            else
                log_warning "Security package missing: $package"
            fi
        done
    else
        log_violation "No virtual environment detected - required for Enhanced Potato Policy"
    fi
}

# Main audit function
run_comprehensive_audit() {
    log_info "Starting Enhanced Potato Policy v$VERSION comprehensive audit"
    echo -e "${CYAN}Framework: Pain → Protocol → Protection${NC}"
    echo ""

    # Run all checks
    check_virtual_environment
    check_ignore_files
    check_sensitive_files
    check_secrets_in_code
    check_git_history
    check_file_permissions

    # Generate summary
    echo "" | tee -a "$LOG_FILE"
    echo "=== AUDIT SUMMARY ===" | tee -a "$LOG_FILE"

    if [ $VIOLATION_COUNT -eq 0 ]; then
        log_success "🥔 Enhanced Potato Policy: ALL CHECKS PASSED"
        log_success "System is compliant with Enhanced Potato Policy v$VERSION"
        echo "Exit code: 0" >> "$LOG_FILE"
        return 0
    else
        log_error "🥔 Enhanced Potato Policy: $VIOLATION_COUNT VIOLATIONS DETECTED"
        log_error "System requires attention to achieve compliance"
        echo "Exit code: 1" >> "$LOG_FILE"
        return 1
    fi
}

# Usage function
show_usage() {
    echo "Enhanced Potato Policy v$VERSION - Comprehensive Security Checker"
    echo "Framework: Pain → Protocol → Protection"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --verbose, -v    Enable verbose output"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Exit codes:"
    echo "  0 - All checks passed"
    echo "  1 - Violations detected"
    echo ""
    echo "Log file: $LOG_FILE"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    init_logging

    if [[ "$VERBOSE" == true ]]; then
        log_info "Verbose mode enabled"
    fi

    run_comprehensive_audit
}

# Execute main function
main "$@"
