# Political Donation Platform - Web Interface

Simple, deployable web interface for browsing the political donation database.

## Features

- 📊 Browse all candidates with strategic metrics
- 🔍 Search by name
- 🎯 Filter by party, state, recommendation tier
- 📈 Sort by impact score
- 💰 View funding gaps and leverage scores
- 🌱 See grassroots support percentage
- 📱 Responsive design (mobile-friendly)

## Quick Start

### 1. Export Database to JSON

From the `prototype3` directory:

```bash
python3 export_to_json.py
```

This creates JSON files in `web-interface/public/`:
- `candidates.json`
- `races.json`
- `issues.json`
- `candidate-issues.json`
- `demographics.json`
- `stats.json`

### 2. Install Dependencies

```bash
cd web-interface
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Deploy to Vercel

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd web-interface
vercel
```

### Option 2: GitHub + Vercel

1. Push to GitHub:
   ```bash
   git add web-interface/
   git commit -m "Add web interface"
   git push
   ```

2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Set root directory to `prototype3/web-interface`
6. Click "Deploy"

### Option 3: Vercel Dashboard

1. Build the static site:
   ```bash
   npm run build
   ```

2. Go to [vercel.com](https://vercel.com)
3. Drag and drop the `out` folder

## Updating Data

When you have new database data:

1. Run the scraper to update the database
2. Export to JSON:
   ```bash
   python3 export_to_json.py
   ```
3. Redeploy:
   ```bash
   vercel --prod
   ```

## Configuration

### Change Port (Development)

Edit `package.json`:
```json
"dev": "next dev -p 3001"
```

### Custom Domain

In Vercel dashboard:
1. Go to your project
2. Settings → Domains
3. Add your custom domain

## File Structure

```
web-interface/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page (candidate browser)
│   └── globals.css         # Global styles
├── public/                 # Static files (JSON data goes here)
│   ├── candidates.json
│   ├── races.json
│   ├── issues.json
│   └── stats.json
├── package.json
├── next.config.js          # Next.js config (static export)
├── tailwind.config.js      # Tailwind CSS config
└── tsconfig.json           # TypeScript config
```

## Features Explained

### Filters

- **Search**: Find candidates by name
- **Party**: Filter by political party
- **State**: Filter by state
- **Recommendation Tier**: High/Medium/Low impact
- **Min Impact Score**: Slider to set minimum score

### Candidate Cards

Each card shows:
- Name and incumbent status
- Office, state, district, party
- Impact score (0-100)
- Leverage score (0-100)
- Total raised
- Funding gap vs opponent
- Grassroots support percentage

### Color Coding

- **Green badges**: High Impact
- **Yellow badges**: Medium Impact
- **Gray badges**: Lower Priority
- **Blue badges**: Incumbent

## Tech Stack

- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Static Export**: No server needed

## Performance

- **Static Site**: Pre-rendered at build time
- **Fast Loading**: All data in JSON files
- **No Database**: Client-side filtering
- **CDN Ready**: Optimized for Vercel Edge Network

## Limitations

- Data is static (updated when you redeploy)
- No real-time updates
- No user accounts or saved filters
- Client-side filtering only (all data loaded)

## Future Enhancements

- [ ] Issue-based filtering
- [ ] Candidate detail pages
- [ ] Race comparison view
- [ ] Export filtered results
- [ ] Save favorite candidates
- [ ] Email alerts for new opportunities
- [ ] Interactive charts and graphs
- [ ] District demographic overlays

## Troubleshooting

### "Cannot find module" errors

```bash
rm -rf node_modules package-lock.json
npm install
```

### Build fails

Check that JSON files exist in `public/`:
```bash
ls public/*.json
```

If missing, run:
```bash
cd ..
python3 export_to_json.py
```

### Vercel deployment fails

Make sure `next.config.js` has:
```js
output: 'export'
```

## Support

For issues or questions:
1. Check that database has data: `python3 test_database.py`
2. Verify JSON export worked: `ls web-interface/public/*.json`
3. Check browser console for errors

## License

Same as parent project.
