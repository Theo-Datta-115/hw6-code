# Vercel Deployment Guide

## Quick Deploy (Recommended)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add vercel.json"
git push personal prototype3:main
```

### Step 2: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repo: `Theo-Datta-115/hw6-code`
4. **IMPORTANT**: Set **Root Directory** to: `web-interface`
5. Framework Preset: Next.js (should auto-detect)
6. Click **Deploy**

That's it! Vercel will:
- Install dependencies
- Build the static site
- Deploy to a URL like: `hw6-code.vercel.app`

## Alternative: Vercel CLI

```bash
cd web-interface

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# For production
vercel --prod
```

## Troubleshooting

### "Not Found" Error

**Cause**: Vercel is looking in the wrong directory

**Fix**: Make sure Root Directory is set to `web-interface` in project settings:
1. Go to your project on Vercel
2. Settings → General
3. Root Directory: `web-interface`
4. Save and redeploy

### Build Fails

**Check**:
1. `package.json` exists in `web-interface/`
2. `next.config.js` has `output: 'export'`
3. JSON files exist in `web-interface/public/`

**Fix**:
```bash
# Make sure data is exported
cd /path/to/prototype3
python3 export_to_json.py

# Verify files exist
ls web-interface/public/*.json
```

### Missing Data

If the site loads but shows no candidates:

```bash
# Re-export database
python3 export_to_json.py

# Commit and push
git add web-interface/public/*.json
git commit -m "Update data"
git push personal prototype3:main
```

Vercel will auto-redeploy.

## Project Structure

```
prototype3/
├── vercel.json              # Tells Vercel where to build
├── web-interface/           # Next.js app (ROOT DIRECTORY for Vercel)
│   ├── app/
│   ├── public/              # JSON data files
│   ├── package.json
│   └── next.config.js
├── database_schema.py       # Python scripts (not deployed)
├── scraper.py
└── export_to_json.py        # Run this to update data
```

## Updating Data

1. Run scraper to get new data:
   ```bash
   python3 scraper.py YOUR_FEC_KEY
   ```

2. Export to JSON:
   ```bash
   python3 export_to_json.py
   ```

3. Commit and push:
   ```bash
   git add web-interface/public/*.json
   git commit -m "Update data"
   git push personal prototype3:main
   ```

4. Vercel auto-deploys (or run `vercel --prod`)

## Environment Variables

None needed! All data is in static JSON files.

## Custom Domain

1. Go to your project on Vercel
2. Settings → Domains
3. Add your domain
4. Follow DNS instructions

## Performance

- **Static Site**: Pre-rendered, no server needed
- **CDN**: Deployed to Vercel Edge Network
- **Fast**: All data loaded from JSON files
- **Free Tier**: Unlimited bandwidth for personal projects

## Success Checklist

✅ Root Directory set to `web-interface`
✅ JSON files in `web-interface/public/`
✅ `next.config.js` has `output: 'export'`
✅ Build succeeds locally: `npm run build`
✅ Vercel deployment shows green checkmark

Your site should be live at: `https://hw6-code.vercel.app`
