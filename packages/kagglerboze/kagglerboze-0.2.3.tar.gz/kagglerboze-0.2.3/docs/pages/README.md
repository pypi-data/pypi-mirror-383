# KagglerBoze GitHub Pages

This directory contains the GitHub Pages site for KagglerBoze.

## 🌐 Live Site

Visit: https://starboze.github.io/kagglerboze

## 📁 Structure

```
docs/pages/
├── index.html          # Main landing page
├── _config.yml         # Jekyll configuration
└── README.md          # This file
```

## 🎨 Features

- **Hero Section**: Compelling value proposition
- **Stats Bar**: Key metrics (96% accuracy, 30min, $5)
- **Use Cases**: Medical, Finance, Legal examples
- **How It Works**: 3-step process
- **Interactive Demo**: Code examples with tabs
- **Comparison Table**: vs Fine-tuning, QLoRA
- **Responsive Design**: Mobile-friendly

## 🚀 Local Development

To preview locally:

```bash
# Install Jekyll
gem install bundler jekyll

# Serve site
cd docs/pages
jekyll serve

# Visit http://localhost:4000
```

## 🔧 Customization

### Update Stats

Edit the stats section in `index.html`:

```html
<div class="stat-item">
    <span class="stat-number">96%</span>
    <div class="stat-label">Accuracy Achieved</div>
</div>
```

### Add Use Case

Add a new card in the use-cases-grid:

```html
<div class="use-case-card">
    <div class="use-case-icon">🎯</div>
    <h3>Your Domain</h3>
    <span class="accuracy">95% Accuracy</span>
    <p>Description...</p>
</div>
```

### Update Demo

Add a new demo tab in the demo section:

```html
<button class="demo-tab" onclick="showDemo('newdemo')">New Demo</button>

<div id="demo-newdemo" class="demo-content">
    <!-- Your demo content -->
</div>
```

## 📊 Analytics

To enable Google Analytics:

1. Get your tracking ID from Google Analytics
2. Update `_config.yml`:
   ```yml
   google_analytics: UA-XXXXXXXXX-X
   ```

## 🎨 Design Tokens

CSS variables defined in `:root`:

```css
--primary: #2563eb;      /* Primary brand color */
--secondary: #10b981;    /* Success/accuracy */
--accent: #f59e0b;       /* Highlights */
--text: #1f2937;        /* Main text */
--bg: #ffffff;          /* Background */
```

## 📱 Responsive Breakpoints

- Desktop: > 768px
- Mobile: ≤ 768px

## 🚀 Deployment

### Automatic Deployment (GitHub Actions)

This project uses GitHub Actions for automatic deployment:

1. **Push changes** to `main` branch (or `feature/github-pages` for testing)
2. **GitHub Actions workflow** (`.github/workflows/gh-pages.yml`) automatically:
   - Checks out the repository
   - Builds the site with Jekyll
   - Deploys to GitHub Pages
3. **Live site** available at: https://starboze.github.io/kagglerboze

The workflow is triggered on:
- Push to `main` branch with changes to `docs/pages/**` or workflow file
- Manual workflow dispatch via GitHub Actions UI

### Enable GitHub Pages (One-time Setup)

**IMPORTANT:** Repository settings must be configured to enable Pages:

1. Go to repository **Settings** > **Pages**
2. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
   - (Not "Deploy from a branch" - we use Actions for build)
3. Click **Save**
4. Wait 2-5 minutes for first deployment
5. Visit https://starboze.github.io/kagglerboze

See `/docs/DEPLOYMENT.md` for detailed setup instructions and troubleshooting.

### Manual Deployment (Alternative)

If you prefer manual deployment without Actions:

```bash
# In repository settings:
# Pages > Source > Deploy from a branch
# Branch: gh-pages, Folder: /root or /docs
```

### Verify Deployment

After enabling Pages and pushing changes:

```bash
# Check workflow status
gh workflow view "Deploy GitHub Pages"

# Check recent runs
gh run list --workflow=gh-pages.yml

# View workflow logs
gh run view --log
```

## 📝 SEO

Optimized meta tags:

- Title: "KagglerBoze - Teach AI Your Expertise in 30 Minutes"
- Description: Domain-specific AI framework
- Open Graph tags for social sharing

## 🎯 Call-to-Actions

Primary CTAs:
- "Get Started Free" → GitHub repo
- "Watch Demo" → Demo section
- "Read Documentation" → Docs

## 📈 Conversion Optimization

Key elements:
1. **Above the fold**: Clear value prop
2. **Social proof**: Stats bar (96%, 30min, $5)
3. **Concrete examples**: Medical, Finance, Legal
4. **Visual demo**: Code examples with output
5. **Comparison**: vs alternatives (fine-tuning)
6. **Final CTA**: Multiple entry points

## 🔗 Links

- Main repo: https://github.com/StarBoze/kagglerboze
- Documentation: /docs/QUICK_START.md
- Issues: /issues
- Discussions: /discussions

## 🎨 Future Enhancements

- [ ] Interactive code playground
- [ ] Video demo embed
- [ ] Testimonials section
- [ ] Blog integration
- [ ] Pricing page (for enterprise)
- [ ] Dark mode toggle
