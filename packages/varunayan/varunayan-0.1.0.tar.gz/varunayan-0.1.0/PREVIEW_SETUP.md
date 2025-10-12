# Documentation Preview Setup

This guide will help you set up automatic documentation preview deployments for pull requests using Netlify.

## Prerequisites

- GitHub repository with documentation
- Netlify account (free tier works perfectly)

## Step 1: Create a Netlify Account

1. Go to [netlify.com](https://netlify.com)
2. Sign up using your GitHub account
3. This will give Netlify access to your repositories

## Step 2: Create a New Netlify Site

1. In your Netlify dashboard, click "Add new site" → "Import an existing project"
2. Choose "GitHub" as your Git provider
3. Select your `varunayan` repository
4. Configure build settings:
   - **Build command**: `cd docs && make html`
   - **Publish directory**: `docs/_build/html`
   - **Base directory**: (leave empty)
5. Click "Deploy site"

## Step 3: Get Your Netlify Credentials

### Get Site ID:
1. Go to your site's dashboard in Netlify
2. Go to "Site settings" → "General"
3. Copy the "Site ID" (looks like: `abc123def-456g-789h-012i-345jklmnop67`)

### Get Auth Token:
1. Go to your Netlify account settings: [app.netlify.com/user/applications](https://app.netlify.com/user/applications)
2. Click "New access token"
3. Give it a name like "GitHub Actions"
4. Copy the generated token (starts with `netlify_`)

## Step 4: Add GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret" and add these two secrets:

   **Secret 1:**
   - Name: `NETLIFY_AUTH_TOKEN`
   - Value: The auth token you copied from Netlify

   **Secret 2:**
   - Name: `NETLIFY_SITE_ID`
   - Value: The site ID you copied from Netlify

## Step 5: Test the Setup

1. Create a new branch: `git checkout -b test-preview`
2. Make a small change to any file in the `docs/` directory
3. Commit and push: `git add . && git commit -m "Test preview" && git push origin test-preview`
4. Create a pull request to the `main` branch
5. The GitHub Action will automatically trigger and deploy a preview
6. You'll see a comment on the PR with the preview link

## How It Works

- **Trigger**: The action runs on every PR that changes files in `docs/`, `varunayan/`, or `pyproject.toml`
- **Build**: Installs dependencies and builds the documentation using Sphinx
- **Deploy**: Uploads the built documentation to Netlify
- **Comment**: Adds a comment to the PR with the preview link

## Features

- ✅ Automatic preview deployments for every PR
- ✅ Comments on PRs with preview links
- ✅ Secure deployment using GitHub secrets
- ✅ Fast builds with dependency caching
- ✅ Clean URLs and proper redirects
- ✅ Security headers and performance optimizations

## Troubleshooting

### Build Fails
- Check the GitHub Actions logs for detailed error messages
- Ensure all dependencies are listed in `requirements-docs.txt`
- Verify the documentation builds locally with `cd docs && make html`

### Preview Link Not Working
- Check that the `NETLIFY_SITE_ID` secret is correct
- Verify the `NETLIFY_AUTH_TOKEN` has the right permissions
- Look for deployment errors in the Netlify dashboard

### No Comment on PR
- Make sure the PR changes files in the watched paths
- Check that the GitHub token has the right permissions
- Verify the action completed successfully

## Optional: Custom Domain

If you want to use a custom domain for previews:

1. Go to Netlify dashboard → "Domain settings"
2. Add your custom domain
3. Update the DNS records as instructed by Netlify
4. Enable HTTPS (automatic with Netlify)

## Cost

- **Netlify**: Free tier includes 100GB bandwidth and 300 build minutes/month
- **GitHub Actions**: Free tier includes 2,000 minutes/month for public repos
- This setup should easily fit within free tier limits for most documentation projects

## Next Steps

Once set up, every PR will automatically get a preview deployment. The preview URL will be commented on the PR and will update with each new commit to the PR branch.

Happy documenting! 📖