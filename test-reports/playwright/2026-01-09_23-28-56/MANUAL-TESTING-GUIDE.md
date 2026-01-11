# Manual Testing Quick Guide
## Integrated Panel Metrics Dashboard

### Quick Start

1. **Open your browser** to http://localhost:5173
2. **Navigate** to Dashboard tab (should be default view)
3. **Scroll down** past the main metrics cards
4. **Locate** the "Enhanced Metrics Section" with 4 new panels

---

## What to Look For

### Section 1: Token Usage (Left Column, Top Row)

**Expected Elements:**
- Header: "Token Usage" with "Last 7 days" badge
- Bar chart showing daily token usage (7 bars)
- Summary box with:
  - Total Tokens (formatted as K or M)
  - Est. Cost (formatted as $X.XX)

**Visual Checks:**
- [ ] Bars are purple (`--accent-primary` color)
- [ ] Bars scale properly (tallest = max usage)
- [ ] Hover shows tooltip with day and token count
- [ ] Summary box has gray background (`--bg-tertiary`)
- [ ] Numbers use monospace font
- [ ] "Last 7 days" badge matches existing pipeline badge style

**Possible States:**
- Loading: Animated skeleton (gray gradient)
- Empty: Chart icon with "No token usage data available"
- Success: Chart with data

---

### Section 2: Cost Analysis (Right Column, Top Row)

**Expected Elements:**
- Header: "Cost Analysis"
- Total Cost display (large number with accent border)
- List of models with:
  - Color indicator dot
  - Model name
  - Cost amount
  - Progress bar (colored by model)
  - Percentage of total

**Visual Checks:**
- [ ] Total cost has left purple border accent
- [ ] Models sorted by cost (highest first)
- [ ] Progress bars match color indicators:
  - Opus: Purple
  - Sonnet: Cyan
  - Haiku: Green
  - GPT-4: Amber
  - GPT-3.5: Pink
- [ ] Hover effect moves row slightly right
- [ ] Percentages add up to ~100%

**Possible States:**
- Loading: Animated skeleton
- Empty: Dollar sign icon with "No cost data available"
- Success: Model breakdown list

---

### Section 3: Execution Performance (Left Column, Bottom Row)

**Expected Elements:**
- Header: "Execution Performance"
- 3 mini cards in grid:
  - Avg Time (clock icon)
  - P95 Time (chart icon)
  - Success % (checkmark icon)
- Recent Executions list (top 3):
  - Status dot (green/red)
  - Command name
  - Duration

**Visual Checks:**
- [ ] 3 cards displayed side-by-side
- [ ] Icons are purple and slightly transparent
- [ ] Values use monospace font
- [ ] Labels are uppercase with letter-spacing
- [ ] Hover lifts cards slightly (translateY)
- [ ] Recent executions show status dots:
  - Green = success
  - Red = error
- [ ] Long command names are truncated with "..."

**Possible States:**
- Loading: Animated skeleton
- Empty: Gauge icon with "No execution data available"
- Success: 3 cards + optional recent list

---

### Section 4: AI Insights (Right Column, Bottom Row)

**Expected Elements:**
- Header: "AI Insights" with count badge
- List of insight cards with:
  - Colored left border
  - Icon matching type
  - Message text
  - Optional metric (label: value)

**Visual Checks:**
- [ ] Count badge shows in amber/orange
- [ ] Border colors match types:
  - Warning: Amber
  - Success: Green
  - Tip: Purple
  - Info: Cyan
- [ ] Icons match types:
  - Warning: Triangle exclamation
  - Success: Circle check
  - Tip: Lightbulb
  - Info: Info circle
- [ ] Hover effect moves card right
- [ ] Metrics use monospace font

**Possible States:**
- Hidden: Section does not appear if no insights
- Empty: Brain icon with "No insights available"
- Success: List of insight cards

---

## Responsive Testing

### Desktop (1920x1080)
```
[Token Usage - wider    ] [Cost Analysis - narrower]
[Execution Metrics      ] [AI Insights (if present)]
```
- [ ] 2-column layout
- [ ] Token Usage ~66% width
- [ ] Cost Analysis ~33% width

### Tablet (768x1024)
```
[Token Usage           ]
[Cost Analysis         ]
[Execution Metrics     ]
[AI Insights           ]
```
- [ ] Stacks to 1-column
- [ ] All sections full width

### Mobile (375x667)
```
[Token Usage           ]
  - Chart (shorter)
  - Stats stack vertically

[Cost Analysis         ]
  - Total cost stacks

[Execution Metrics     ]
  - 3 cards stack vertically

[AI Insights           ]
  - Same as desktop
```
- [ ] 1-column layout
- [ ] Execution cards stack
- [ ] Chart height reduced
- [ ] All text remains legible

---

## Color Consistency Check

Open browser DevTools (F12) and inspect elements:

### Backgrounds
- [ ] Main panels: `background: var(--bg-secondary)`
- [ ] Inner elements: `background: var(--bg-tertiary)`
- [ ] Hover states: `background: var(--bg-elevated)`

### Borders
- [ ] Panel borders: `border: 1px solid var(--border-default)`
- [ ] Dividers: `border: 1px solid var(--border-subtle)`

### Text
- [ ] Titles: `color: var(--text-primary)`
- [ ] Body text: `color: var(--text-secondary)`
- [ ] Labels: `color: var(--text-tertiary)`

### Accents
- [ ] Primary (purple): `var(--accent-primary)`
- [ ] Success (green): `var(--accent-success)`
- [ ] Warning (amber): `var(--accent-warning)`
- [ ] Error (red): `var(--accent-error)`

---

## Common Issues to Check

### Layout Issues
- [ ] No horizontal scrollbars
- [ ] No overlapping elements
- [ ] Proper spacing between sections
- [ ] Consistent alignment

### Loading Issues
- [ ] Skeletons appear briefly on page load
- [ ] Skeletons animate smoothly
- [ ] Data appears after loading
- [ ] No "flash of unstyled content"

### Data Issues
- [ ] Numbers format correctly (1.5K not 1500)
- [ ] Currency shows 2 decimals ($10.00 not $10)
- [ ] Percentages show 1 decimal (95.5% not 95.50%)
- [ ] Dates/times format consistently

### Interaction Issues
- [ ] Hover effects work smoothly
- [ ] Tooltips appear on hover (chart bars)
- [ ] No console errors
- [ ] No React warnings

---

## API Verification

Open browser console (F12 → Network tab):

### Expected API Calls (on page load)
1. `GET /api/metrics/tokens?projectId=current&period=7d&groupBy=day`
2. `GET /api/metrics/costs?projectId=current&groupBy=model`
3. `GET /api/metrics/execution?projectId=current`
4. `GET /api/metrics/insights?projectId=current`

### Check:
- [ ] All 4 calls made in parallel
- [ ] Status 200 OK for all
- [ ] Responses contain valid JSON
- [ ] Auto-refresh happens every 30 seconds

### If APIs fail:
- [ ] Empty states should appear
- [ ] No infinite loading
- [ ] Console shows error message
- [ ] Page remains functional

---

## Screenshot Checklist

Save these screenshots to the test report folder:

Desktop Views:
- [ ] `01-full-homepage.png` - Scroll to show all sections
- [ ] `02-token-usage-panel.png` - Close-up of token chart
- [ ] `03-cost-breakdown.png` - Close-up of cost breakdown
- [ ] `04-execution-metrics.png` - Close-up of execution stats
- [ ] `05-ai-insights.png` - Close-up of insights (if available)
- [ ] `06-hover-effects.png` - Hovering over an element

Responsive Views:
- [ ] `07-mobile-view.png` - Set viewport to 375x667
- [ ] `08-tablet-view.png` - Set viewport to 768x1024

Special States:
- [ ] `09-loading-state.png` - Refresh page and capture quickly
- [ ] `10-empty-states.png` - If no data, capture empty states

---

## Quick Pass/Fail Criteria

### PASS if:
✅ All 4 sections visible
✅ Data loads successfully
✅ Styling matches existing dashboard
✅ Responsive design works
✅ No console errors

### FAIL if:
❌ Sections missing or broken
❌ Infinite loading state
❌ Styling inconsistencies
❌ Layout breaks on mobile
❌ Console errors present

---

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest, if on Mac)
- [ ] Edge (latest)

Expected: Identical appearance and behavior on all browsers.

---

## Accessibility Quick Check

- [ ] All sections have proper headings
- [ ] Colors have sufficient contrast
- [ ] Charts are not the only way to convey info (numbers provided)
- [ ] Icons have text labels
- [ ] No motion sickness triggers (animations are subtle)

---

## Time Estimate

- Basic visual check: 5 minutes
- Detailed inspection: 15 minutes
- Responsive testing: 10 minutes
- Screenshots: 10 minutes
- **Total: ~40 minutes**

---

## Reporting Issues

If you find issues, note:
1. **What:** Description of the issue
2. **Where:** Which panel/section
3. **Expected:** What should happen
4. **Actual:** What actually happens
5. **Browser:** Which browser/version
6. **Viewport:** Screen size if responsive issue
7. **Screenshot:** Visual evidence

---

## Success Checklist

After testing, verify:
- [ ] All sections render correctly
- [ ] Data displays properly
- [ ] Styling is consistent
- [ ] Responsive design works
- [ ] No errors in console
- [ ] Auto-refresh works
- [ ] Screenshots captured
- [ ] Issues documented (if any)

---

**Happy Testing!**

For full validation report, see: `validation-report-integrated-metrics-dashboard.md`
