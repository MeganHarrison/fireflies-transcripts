# GitHub Actions Setup Guide for Fireflies Sync

## 📋 Prerequisites

Before setting up the GitHub Actions, you need to add your API keys as secrets to your GitHub repository.

## 🔐 Step 1: Add Repository Secrets

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/fireflies-transcripts`
2. Click on **Settings** (in the repository, not your profile)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each of these:

### Required Secrets:

| Secret Name | Value | Where to Find It |
|------------|-------|------------------|
| `FIREFLIES_API_KEY` | Your Fireflies API key | From your .env file or Fireflies settings |
| `OPENAI_API_KEY` | Your OpenAI API key | From your .env file or OpenAI dashboard |
| `SUPABASE_URL` | Your Supabase project URL | From your .env file |
| `SUPABASE_SERVICE_KEY` | Your Supabase service role key | From your .env file |

## 🚀 Step 2: Understanding the Workflows

### 1. **Scheduled Sync** (`sync-fireflies.yml`)
- **Runs automatically every 6 hours**
- Syncs all new transcripts from Fireflies
- Can also be triggered manually with options:
  - Sync all transcripts
  - Test mode (sync one transcript)
  - Sync specific transcript by ID

### 2. **Webhook Sync** (`webhook-sync.yml`)
- **Triggered by webhook from Fireflies**
- Syncs individual transcripts immediately after meetings
- Near real-time updates

## 🎯 Step 3: Manual Trigger

### To manually run the sync:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Sync Fireflies Transcripts**
4. Click **Run workflow**
5. Choose your options:
   - **Sync mode**: all, test, or specific
   - **Transcript ID**: (only needed for specific mode)
6. Click **Run workflow**

## 🪝 Step 4: Setting up Fireflies Webhook (Optional)

### To get real-time syncs after each meeting:

1. **Get your webhook URL**:
   ```
   https://api.github.com/repos/YOUR_USERNAME/fireflies-transcripts/dispatches
   ```

2. **Create a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create a token with `repo` scope
   - Save this token securely

3. **Configure Fireflies Webhook**:
   - Go to Fireflies.ai settings
   - Add a webhook with this configuration:
   ```json
   {
     "url": "https://api.github.com/repos/YOUR_USERNAME/fireflies-transcripts/dispatches",
     "method": "POST",
     "headers": {
       "Accept": "application/vnd.github.v3+json",
       "Authorization": "Bearer YOUR_GITHUB_TOKEN",
       "Content-Type": "application/json"
     },
     "body": {
       "event_type": "fireflies-webhook",
       "client_payload": {
         "transcript_id": "{{transcript_id}}"
       }
     }
   }
   ```

## 📊 Step 5: Monitoring

### Check sync status:
1. Go to the **Actions** tab in your repository
2. Click on any workflow run to see:
   - Logs from the sync process
   - Any errors that occurred
   - Downloaded transcript files (as artifacts)

### Workflow Status Badges:
Add these to your README.md:

```markdown
![Sync Status](https://github.com/YOUR_USERNAME/fireflies-transcripts/actions/workflows/sync-fireflies.yml/badge.svg)
![Webhook Status](https://github.com/YOUR_USERNAME/fireflies-transcripts/actions/workflows/webhook-sync.yml/badge.svg)
```

## 🔧 Customization Options

### Change sync frequency:
Edit `.github/workflows/sync-fireflies.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Current: every 6 hours
  # Examples:
  # - cron: '0 */12 * * *'  # Every 12 hours
  # - cron: '0 0 * * *'     # Daily at midnight
  # - cron: '0 0 * * 1'     # Weekly on Mondays
```

### Adjust timeout:
```yaml
timeout-minutes: 30  # Increase if you have many transcripts
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Check that all secrets are correctly set
   - Ensure there are no extra spaces in secret values

2. **"Module not found"**
   - Check that requirements.txt includes all dependencies
   - May need to add `pip install numpy tiktoken` explicitly

3. **"Timeout"**
   - Increase `timeout-minutes` in workflow
   - Consider syncing in smaller batches

4. **"Rate limit exceeded"**
   - The script has built-in rate limiting
   - If still hitting limits, increase sleep times in the Python script

## 📈 Next Steps

1. **Test the setup**:
   ```bash
   # Locally first
   python scripts/sync/optimized_pipeline.py --test
   
   # Then trigger GitHub Action manually
   ```

2. **Monitor first automated run**:
   - Check Actions tab after first scheduled run
   - Review logs for any issues

3. **Set up notifications** (optional):
   - GitHub can email you if workflows fail
   - Settings → Notifications → Actions

## 💡 Pro Tips

- Start with manual triggers to test
- Use "test" mode first before full sync
- Check artifacts for downloaded transcripts
- Review logs regularly for optimization opportunities
- Consider implementing incremental backups

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Expression Generator](https://crontab.guru/)
- [GitHub Webhooks Guide](https://docs.github.com/en/developers/webhooks-and-events)
