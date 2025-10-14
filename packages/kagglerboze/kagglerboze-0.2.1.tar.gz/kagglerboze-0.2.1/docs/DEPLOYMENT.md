# GitHub Pages Deployment Guide

This document provides comprehensive instructions for enabling and deploying KagglerBoze's GitHub Pages site.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Enabling GitHub Pages](#enabling-github-pages)
- [Deployment Workflow](#deployment-workflow)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Custom Domain Setup](#custom-domain-setup)
- [Maintenance](#maintenance)

---

## Prerequisites

Before enabling GitHub Pages, ensure you have:

1. **Repository Access**: Admin or write access to the repository
2. **GitHub Actions**: Enabled in repository settings (Settings > Actions > General)
3. **Workflow File**: `.github/workflows/gh-pages.yml` exists in the repository
4. **Content**: `docs/pages/` directory contains:
   - `index.html` - Main landing page
   - `_config.yml` - Jekyll configuration
   - `assets/` - Images and resources (including `og-image.png`)

## Enabling GitHub Pages

### Step 1: Access Repository Settings

1. Navigate to your repository on GitHub: `https://github.com/StarBoze/kagglerboze`
2. Click **Settings** (tab at the top of the repository)
3. Scroll down to the **Pages** section in the left sidebar

### Step 2: Configure GitHub Pages

1. Under **"Build and deployment"**, configure the following:

   **Source:** Select **"GitHub Actions"**

   ⚠️ **Important:** Do NOT select "Deploy from a branch" - we use GitHub Actions for automated builds.

2. Click **Save** if prompted

3. The page will show:
   ```
   Your site is ready to be published at https://starboze.github.io/kagglerboze
   ```

### Step 3: Trigger First Deployment

The GitHub Actions workflow will automatically trigger on:
- Push to `main` branch with changes to `docs/pages/**`
- Manual workflow dispatch

To manually trigger the workflow:

```bash
# Via GitHub CLI
gh workflow run gh-pages.yml

# Or via GitHub web UI:
# Actions > Deploy GitHub Pages > Run workflow
```

### Step 4: Wait for Deployment

1. Go to **Actions** tab in your repository
2. Watch the "Deploy GitHub Pages" workflow
3. Wait for ✅ green checkmark (typically 2-5 minutes)
4. Click on the workflow run to see detailed logs

### Step 5: Verify Site is Live

Visit the deployed site:

**Expected URL:** https://starboze.github.io/kagglerboze

The site should display the KagglerBoze landing page with:
- Hero section with value proposition
- Stats bar (96% accuracy, 30min, $5)
- Use cases (Medical, Finance, Legal)
- Interactive demo tabs
- Comparison table
- Call-to-action buttons

## Deployment Workflow

### Automatic Deployment

The `.github/workflows/gh-pages.yml` workflow automatically deploys on:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'docs/pages/**'
      - '.github/workflows/gh-pages.yml'
  workflow_dispatch:
```

**What happens during deployment:**

1. **Checkout**: Repository code is checked out
2. **Setup Pages**: GitHub Pages environment is configured
3. **Build with Jekyll**: `docs/pages/` directory is built using Jekyll
4. **Upload Artifact**: Built site is uploaded as artifact
5. **Deploy**: Artifact is deployed to GitHub Pages environment

### Manual Deployment

To manually deploy:

```bash
# Using GitHub CLI
gh workflow run gh-pages.yml

# Check workflow status
gh run list --workflow=gh-pages.yml

# View logs of latest run
gh run view --log
```

Or via GitHub web interface:
1. Go to **Actions** tab
2. Select **Deploy GitHub Pages** workflow
3. Click **Run workflow** dropdown
4. Select `main` branch
5. Click **Run workflow** button

## Verification

### 1. Check Deployment Status

```bash
# List recent workflow runs
gh run list --workflow=gh-pages.yml --limit 5

# View specific run details
gh run view <run-id>

# View workflow logs
gh run view <run-id> --log
```

### 2. Verify Site Content

Visit https://starboze.github.io/kagglerboze and check:

- ✅ Page loads without errors
- ✅ All CSS styles are applied
- ✅ Navigation and CTAs work
- ✅ Demo tabs switch correctly
- ✅ Images load (including OG image)
- ✅ Links to GitHub repo work

### 3. Test Social Sharing

Use these tools to verify Open Graph and Twitter Cards:

- **Facebook Debugger**: https://developers.facebook.com/tools/debug/
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator
- **LinkedIn Post Inspector**: https://www.linkedin.com/post-inspector/

Enter your URL: `https://starboze.github.io/kagglerboze`

Expected metadata:
- **Title**: KagglerBoze - Domain-Specific AI
- **Description**: Teach AI Your Expertise in 30 Minutes
- **Image**: OG image (1200x630px) showing "KagglerBoze" branding

### 4. Test Mobile Responsiveness

- Use Chrome DevTools (F12 > Device Toolbar)
- Test on actual mobile devices
- Check breakpoint at 768px

## Troubleshooting

### Issue: "404 - Site not found"

**Possible causes:**
1. GitHub Pages not enabled in Settings
2. Workflow hasn't run yet
3. Deployment failed

**Solutions:**
```bash
# Check if Pages is enabled
gh api repos/:owner/:repo/pages

# Check workflow status
gh run list --workflow=gh-pages.yml

# View workflow logs for errors
gh run view --log

# Re-run failed workflow
gh run rerun <run-id>
```

### Issue: "Workflow fails with 'permission denied'"

**Cause:** Insufficient workflow permissions

**Solution:**
1. Go to **Settings > Actions > General**
2. Under **Workflow permissions**, select:
   - ✅ "Read and write permissions"
3. Under **Workflow permissions**, ensure:
   - ✅ "Allow GitHub Actions to create and approve pull requests"
4. Save changes and re-run workflow

### Issue: "Assets not loading (images, CSS)"

**Cause:** Incorrect asset paths

**Solution:**
- Ensure all asset paths are relative or absolute with correct baseurl
- In `_config.yml`, verify:
  ```yaml
  baseurl: "/kagglerboze"
  url: "https://starboze.github.io"
  ```
- Update image paths in `index.html` if needed:
  ```html
  <img src="assets/og-image.png" alt="...">
  ```

### Issue: "Workflow runs but site not updated"

**Cause:** Workflow succeeded but changes not visible

**Solutions:**
1. **Clear browser cache**: Ctrl+Shift+R (hard refresh)
2. **Check workflow logs**: Ensure build step completed
3. **Wait 5-10 minutes**: GitHub CDN may take time to update
4. **Verify artifact**: Check if artifact was uploaded in workflow run

### Issue: "Jekyll build fails"

**Cause:** Syntax error in `_config.yml` or incompatible Jekyll features

**Solution:**
```bash
# Test Jekyll build locally
cd docs/pages
gem install bundler jekyll
jekyll build

# Check for errors in output
# Fix any YAML syntax errors in _config.yml
```

### Issue: "OG image not showing in social previews"

**Cause:** Image path incorrect or image not deployed

**Solutions:**
1. Verify image exists: https://starboze.github.io/kagglerboze/assets/og-image.png
2. Check meta tag in `index.html`:
   ```html
   <meta property="og:image" content="https://starboze.github.io/kagglerboze/assets/og-image.png">
   ```
3. Validate with Facebook Debugger (it crawls and caches)
4. Wait for cache to expire or use "Scrape Again" button

## Custom Domain Setup

To use a custom domain (e.g., `kagglerboze.com`):

### Step 1: Configure GitHub Pages

1. Go to **Settings > Pages**
2. Under **Custom domain**, enter your domain: `kagglerboze.com`
3. Click **Save**
4. GitHub will create a `CNAME` file in the `gh-pages` branch

### Step 2: Configure DNS

Add DNS records with your domain registrar:

**For apex domain (kagglerboze.com):**
```
A     @     185.199.108.153
A     @     185.199.109.153
A     @     185.199.110.153
A     @     185.199.111.153
```

**For subdomain (www.kagglerboze.com):**
```
CNAME www   starboze.github.io
```

### Step 3: Enable HTTPS

1. Wait for DNS to propagate (up to 48 hours)
2. In **Settings > Pages**, check **Enforce HTTPS**
3. GitHub will automatically provision SSL certificate via Let's Encrypt

### Step 4: Update URLs

Update all hardcoded URLs in:
- `docs/pages/index.html` (og:image, twitter:image)
- `docs/pages/_config.yml` (url, baseurl)

## Maintenance

### Updating Content

1. **Edit files** in `docs/pages/`
2. **Commit and push** to `main` branch
3. **Workflow runs automatically**
4. **Site updates** within 2-5 minutes

```bash
# Example workflow
git checkout main
# Edit docs/pages/index.html
git add docs/pages/
git commit -m "docs: update landing page content"
git push origin main

# Watch deployment
gh run watch
```

### Monitoring Deployments

Set up notifications for failed deployments:

1. Go to **Settings > Notifications**
2. Enable **Actions** notifications
3. Choose notification method (email, mobile)

Or use GitHub CLI:

```bash
# Watch workflow in real-time
gh run watch

# Get notified on completion
gh run watch && echo "Deployment complete!" | notify-send
```

### Performance Optimization

#### Image Optimization

```bash
# Optimize PNG images
pngquant docs/pages/assets/*.png --quality=65-80 --ext .png --force

# Or use ImageOptim (macOS) or TinyPNG (web)
```

#### Minify Assets

For production, consider minifying HTML/CSS:

```bash
# Install html-minifier
npm install -g html-minifier

# Minify HTML
html-minifier --collapse-whitespace --remove-comments \
  docs/pages/index.html -o docs/pages/index.min.html
```

### Analytics

To track site visitors:

1. **Create Google Analytics account**
2. **Get tracking ID**: G-XXXXXXXXXX
3. **Update `_config.yml`**:
   ```yaml
   google_analytics: G-XXXXXXXXXX
   ```
4. **Or add directly to `index.html`**:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```

## Security Considerations

### Workflow Permissions

The workflow requires these permissions (already configured):

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

### Secrets

No secrets are required for GitHub Pages deployment. Avoid committing:
- API keys
- Private tokens
- Environment variables with sensitive data

Use GitHub Secrets for any sensitive data:

```bash
# Add secret via GitHub CLI
gh secret set MY_SECRET < secret.txt
```

## Additional Resources

- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **Jekyll Documentation**: https://jekyllrb.com/docs/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Custom Domains**: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site

## Support

If you encounter issues not covered in this guide:

1. **Check GitHub Status**: https://www.githubstatus.com/
2. **Search Issues**: https://github.com/StarBoze/kagglerboze/issues
3. **Create New Issue**: Include workflow logs and error messages
4. **Community**: Join discussions at https://github.com/StarBoze/kagglerboze/discussions

---

**Last Updated**: 2025-10-13
**Maintained By**: KagglerBoze Team
