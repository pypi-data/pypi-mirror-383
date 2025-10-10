# Orbyt

A minimal CLI tool for analyzing job-related emails from Gmail.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Orbyt:**
   ```bash
   pip install -e .
   ```

3. **Get Gmail API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json`
   - Place it at `~/.orbyt/credentials.json`

## Usage

### Authenticate with Gmail
```bash
orbyt auth
```

### Sync emails
```bash
orbyt sync
```

Optional: specify max results
```bash
orbyt sync --max-results 50
```

### View statistics
```bash
orbyt stats
```

## Email Categories

- **Application Sent** - Application confirmations
- **Interview** - Interview invitations, scheduling
- **Offer** - Job offers
- **Rejection** - Rejections

## Data Storage

All data is stored locally in SQLite at `~/.orbyt/emails.db`

