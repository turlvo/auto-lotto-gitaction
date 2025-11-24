# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated Korean lottery (Lotto) purchasing and result-checking system using GitHub Actions. The system automatically purchases lottery tickets every Friday at 8:50 AM KST and checks results every Saturday at 10:20 PM KST through the 동행복권 (Dhlottery) website.

## Core Architecture

### Main Components

1. **buy_lotto.py**: Automated lottery ticket purchasing script
   - Uses Playwright for browser automation
   - Handles login, balance checking, and ticket purchase
   - Creates GitHub issues for purchase confirmation

2. **check_result.py**: Lottery result checking script
   - Retrieves winning numbers from Dhlottery website
   - Compares purchased tickets with winning numbers
   - Updates GitHub issues with results (🎉 for wins, ☠️ for losses)

### GitHub Actions Workflows

- **action.yml**: Scheduled lottery purchase workflow (Fridays 8:50 AM KST)
- **action-result.yml**: Scheduled result checking workflow (Saturdays 10:20 PM KST)

### Integration Points

- **GitHub Issues API**: Used for notifications and tracking
  - Purchase confirmations create new issues
  - Result checking updates issue labels
- **Playwright**: Web automation for Dhlottery interactions
- **GitHub Secrets**: Stores sensitive credentials (USER_ID, USER_PW, GITHUB_TOKEN, etc.)

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv lotto

# Activate virtual environment
source lotto/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Running Scripts Locally
```bash
# Buy lottery tickets (requires arguments)
python buy_lotto.py <USER_ID> <USER_PW> <BUY_COUNT> <GITHUB_TOKEN> <GIT_OWNER> <GIT_REPO_NAME>

# Check lottery results
python check_result.py <USER_ID> <USER_PW> <GITHUB_TOKEN> <GIT_OWNER> <GIT_REPO_NAME>
```

### Linting
```bash
# Run flake8 for Python linting
flake8 *.py
```

### Testing GitHub Actions
To test the GitHub Actions workflow:
1. Modify `.github/workflows/action.yml` to include `on: [push]`
2. Push changes to trigger the workflow
3. Check GitHub Actions tab for execution results

## Key Implementation Details

### Error Handling
- **BalanceError**: Custom exception for insufficient balance scenarios
- GitHub Issues created for both successful purchases and errors
- Retry logic for result parsing (up to 3 attempts)

### Time Handling
- All times converted to KST (UTC+9)
- Cron schedules in workflows use UTC time

### Security Considerations
- All credentials stored as GitHub Secrets
- No sensitive information in code or commits
- Browser runs in headless mode for security

### Notification System
- Purchase notifications: Creates GitHub issue with purchase details and ticket numbers
- Result notifications: Updates issue labels based on win/loss status
- Issue labels: `:hourglass:` (pending), `:tada:` (win), `:skull_and_crossbones:` (loss)