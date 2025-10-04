---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## ❌ Actual Behavior
A clear and concise description of what actually happened.

## 📷 Screenshots
If applicable, add screenshots to help explain your problem.

## 💻 Environment Information
**Please complete the following information:**
- OS: [e.g. Ubuntu 22.04, macOS 13.0, Windows 11]
- Python Version: [e.g. 3.11.5]
- Project Version: [e.g. main branch, v1.0.0]
- Docker Version (if applicable): [e.g. 24.0.0]

**Python Package Versions:**
```bash
# Run this command and paste the output:
pip list | grep -E "(whisper|torch|numpy|ffmpeg)"
```

## 🔍 Additional Context
Add any other context about the problem here.

### Error Logs
```
Paste any relevant error messages or logs here
```

### Configuration
```python
# If applicable, share your configuration or command that caused the issue
python transcribe.py audio.mp3 --model small --language en
```

## 🩹 Possible Solution
If you have ideas on how to fix this issue, please describe them here.

## 📋 Checklist
- [ ] I have searched for similar issues
- [ ] I have provided all requested information
- [ ] I have tested with the latest version
- [ ] I have included error logs (if applicable)
