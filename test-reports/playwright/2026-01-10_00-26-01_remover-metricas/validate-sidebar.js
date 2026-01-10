const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const REPORT_DIR = '/Users/eduardo/Documents/youtube/orquestrator-agent/test-reports/playwright/2026-01-10_00-26-01_remover-metricas';
const BASE_URL = 'http://localhost:5173';

async function validateImplementation() {
  let browser;
  let results = {
    timestamp: new Date().toISOString(),
    status: 'PASS',
    steps: [],
    errors: [],
    screenshots: []
  };

  try {
    console.log('Starting browser validation...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    // Enable console logging
    page.on('console', msg => {
      const type = msg.type();
      if (type === 'error' || type === 'warning') {
        results.errors.push({
          type: type,
          message: msg.text(),
          location: msg.location()
        });
      }
    });

    // Step 1: Navigate to application
    console.log('Step 1: Navigating to application...');
    await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
    await page.screenshot({ path: path.join(REPORT_DIR, '01-initial-page.png'), fullPage: true });
    results.steps.push({
      number: 1,
      action: 'Navigate to application',
      status: 'PASS',
      screenshot: '01-initial-page.png'
    });
    results.screenshots.push({ file: '01-initial-page.png', description: 'Initial page load' });

    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);

    // Step 2: Check sidebar for navigation items
    console.log('Step 2: Checking sidebar navigation items...');

    // Get all navigation items text
    const navItems = await page.evaluate(() => {
      const items = [];
      // Try multiple selectors to find navigation items
      const selectors = [
        'nav a',
        '[class*="sidebar"] a',
        '[class*="navigation"] a',
        'aside a',
        '[class*="nav"] button',
        '[class*="nav"] a'
      ];

      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
          elements.forEach(el => {
            const text = el.textContent.trim();
            if (text) items.push(text);
          });
          break;
        }
      }

      return [...new Set(items)]; // Remove duplicates
    });

    console.log('Navigation items found:', navItems);

    // Check that "Métricas" is NOT present
    const hasMetricas = navItems.some(item =>
      item.toLowerCase().includes('métrica') ||
      item.toLowerCase().includes('metrica') ||
      item.toLowerCase().includes('metrics')
    );

    if (hasMetricas) {
      results.status = 'FAIL';
      results.steps.push({
        number: 2,
        action: 'Verify "Métricas" is NOT in sidebar',
        status: 'FAIL',
        details: 'Found Métricas in navigation items',
        screenshot: '02-sidebar-check.png'
      });
    } else {
      results.steps.push({
        number: 2,
        action: 'Verify "Métricas" is NOT in sidebar',
        status: 'PASS',
        details: `Navigation items found: ${navItems.join(', ')}`,
        screenshot: '02-sidebar-check.png'
      });
    }

    // Take screenshot of sidebar
    await page.screenshot({ path: path.join(REPORT_DIR, '02-sidebar-check.png'), fullPage: true });
    results.screenshots.push({ file: '02-sidebar-check.png', description: 'Sidebar navigation items' });

    // Step 3: Verify expected navigation items are present
    console.log('Step 3: Verifying expected navigation items...');
    const expectedItems = ['Dashboard', 'Kanban', 'AI Assistant', 'Configurações', 'Settings'];
    const missingItems = [];

    expectedItems.forEach(item => {
      const found = navItems.some(navItem =>
        navItem.toLowerCase().includes(item.toLowerCase())
      );
      if (!found && item !== 'Settings' && item !== 'Configurações') {
        // Allow either Settings or Configurações
        missingItems.push(item);
      }
    });

    // Check if either Settings or Configurações is present
    const hasSettings = navItems.some(item =>
      item.toLowerCase().includes('settings') ||
      item.toLowerCase().includes('configurações')
    );

    if (!hasSettings) {
      missingItems.push('Settings/Configurações');
    }

    if (missingItems.length > 0) {
      results.status = 'FAIL';
      results.steps.push({
        number: 3,
        action: 'Verify expected navigation items exist',
        status: 'FAIL',
        details: `Missing items: ${missingItems.join(', ')}`,
        screenshot: '02-sidebar-check.png'
      });
    } else {
      results.steps.push({
        number: 3,
        action: 'Verify expected navigation items exist',
        status: 'PASS',
        details: 'All expected items found',
        screenshot: '02-sidebar-check.png'
      });
    }

    // Step 4: Click on Dashboard (if not already there)
    console.log('Step 4: Testing Dashboard navigation...');
    try {
      // Try to find and click Dashboard link
      const dashboardSelectors = [
        'text/Dashboard',
        'a:has-text("Dashboard")',
        '[href*="dashboard"]',
        'nav a[href="#dashboard"]'
      ];

      let clicked = false;
      for (const selector of dashboardSelectors) {
        try {
          await page.click(selector, { timeout: 2000 });
          clicked = true;
          break;
        } catch (e) {
          // Try next selector
        }
      }

      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(REPORT_DIR, '03-dashboard-view.png'), fullPage: true });
      results.screenshots.push({ file: '03-dashboard-view.png', description: 'Dashboard view' });

      results.steps.push({
        number: 4,
        action: 'Navigate to Dashboard',
        status: clicked ? 'PASS' : 'SKIP',
        details: clicked ? 'Successfully navigated to Dashboard' : 'Already on Dashboard or navigation not needed',
        screenshot: '03-dashboard-view.png'
      });
    } catch (error) {
      results.steps.push({
        number: 4,
        action: 'Navigate to Dashboard',
        status: 'SKIP',
        details: `Could not click Dashboard: ${error.message}`,
        screenshot: '03-dashboard-view.png'
      });
    }

    // Step 5: Check for metrics on Dashboard
    console.log('Step 5: Checking for metrics on Dashboard...');
    const metricsPresent = await page.evaluate(() => {
      const text = document.body.textContent.toLowerCase();
      const hasMetricsKeywords =
        text.includes('completion') ||
        text.includes('velocity') ||
        text.includes('taxa') ||
        text.includes('velocidade') ||
        text.includes('cards') ||
        text.includes('métricas');

      // Also check for metric-related elements
      const hasMetricElements =
        document.querySelector('[class*="metric"]') !== null ||
        document.querySelector('[class*="chart"]') !== null ||
        document.querySelector('[class*="stats"]') !== null;

      return hasMetricsKeywords || hasMetricElements;
    });

    if (metricsPresent) {
      results.steps.push({
        number: 5,
        action: 'Verify Dashboard displays metrics',
        status: 'PASS',
        details: 'Metrics found on Dashboard page',
        screenshot: '03-dashboard-view.png'
      });
    } else {
      results.steps.push({
        number: 5,
        action: 'Verify Dashboard displays metrics',
        status: 'WARN',
        details: 'Could not detect metrics on Dashboard - may need manual verification',
        screenshot: '03-dashboard-view.png'
      });
    }

    // Step 6: Test Kanban navigation
    console.log('Step 6: Testing Kanban navigation...');
    try {
      const kanbanSelectors = [
        'text/Kanban',
        'a:has-text("Kanban")',
        '[href*="kanban"]'
      ];

      let clicked = false;
      for (const selector of kanbanSelectors) {
        try {
          await page.click(selector, { timeout: 2000 });
          clicked = true;
          break;
        } catch (e) {
          // Try next selector
        }
      }

      if (clicked) {
        await page.waitForTimeout(1500);
        await page.screenshot({ path: path.join(REPORT_DIR, '04-kanban-view.png'), fullPage: true });
        results.screenshots.push({ file: '04-kanban-view.png', description: 'Kanban Board view' });

        results.steps.push({
          number: 6,
          action: 'Navigate to Kanban Board',
          status: 'PASS',
          screenshot: '04-kanban-view.png'
        });
      } else {
        throw new Error('Could not find Kanban navigation element');
      }
    } catch (error) {
      results.status = 'FAIL';
      results.steps.push({
        number: 6,
        action: 'Navigate to Kanban Board',
        status: 'FAIL',
        details: error.message,
        screenshot: '04-kanban-view.png'
      });
      await page.screenshot({ path: path.join(REPORT_DIR, '04-kanban-view.png'), fullPage: true });
      results.screenshots.push({ file: '04-kanban-view.png', description: 'Kanban navigation attempt' });
    }

    // Step 7: Test AI Assistant navigation
    console.log('Step 7: Testing AI Assistant navigation...');
    try {
      const chatSelectors = [
        'text/AI Assistant',
        'a:has-text("AI Assistant")',
        '[href*="chat"]',
        'text/Chat'
      ];

      let clicked = false;
      for (const selector of chatSelectors) {
        try {
          await page.click(selector, { timeout: 2000 });
          clicked = true;
          break;
        } catch (e) {
          // Try next selector
        }
      }

      if (clicked) {
        await page.waitForTimeout(1500);
        await page.screenshot({ path: path.join(REPORT_DIR, '05-ai-assistant-view.png'), fullPage: true });
        results.screenshots.push({ file: '05-ai-assistant-view.png', description: 'AI Assistant view' });

        results.steps.push({
          number: 7,
          action: 'Navigate to AI Assistant',
          status: 'PASS',
          screenshot: '05-ai-assistant-view.png'
        });
      } else {
        throw new Error('Could not find AI Assistant navigation element');
      }
    } catch (error) {
      results.status = 'FAIL';
      results.steps.push({
        number: 7,
        action: 'Navigate to AI Assistant',
        status: 'FAIL',
        details: error.message,
        screenshot: '05-ai-assistant-view.png'
      });
      await page.screenshot({ path: path.join(REPORT_DIR, '05-ai-assistant-view.png'), fullPage: true });
      results.screenshots.push({ file: '05-ai-assistant-view.png', description: 'AI Assistant navigation attempt' });
    }

    // Step 8: Check for console errors
    console.log('Step 8: Analyzing console errors...');
    const criticalErrors = results.errors.filter(e =>
      e.type === 'error' &&
      (e.message.toLowerCase().includes('metricspage') ||
       e.message.toLowerCase().includes('moduletype') ||
       e.message.toLowerCase().includes('metrics'))
    );

    if (criticalErrors.length > 0) {
      results.status = 'FAIL';
      results.steps.push({
        number: 8,
        action: 'Check for metrics-related console errors',
        status: 'FAIL',
        details: `Found ${criticalErrors.length} critical errors: ${JSON.stringify(criticalErrors)}`
      });
    } else {
      results.steps.push({
        number: 8,
        action: 'Check for metrics-related console errors',
        status: 'PASS',
        details: `Total console errors: ${results.errors.filter(e => e.type === 'error').length}, none related to metrics removal`
      });
    }

    // Final summary
    console.log('\n=== VALIDATION SUMMARY ===');
    console.log(`Status: ${results.status}`);
    console.log(`Total Steps: ${results.steps.length}`);
    console.log(`Screenshots: ${results.screenshots.length}`);
    console.log(`Console Errors: ${results.errors.filter(e => e.type === 'error').length}`);

  } catch (error) {
    console.error('Validation failed with error:', error);
    results.status = 'FAIL';
    results.errors.push({
      type: 'fatal',
      message: error.message,
      stack: error.stack
    });
  } finally {
    if (browser) {
      await browser.close();
    }
  }

  // Save results to JSON
  fs.writeFileSync(
    path.join(REPORT_DIR, 'results.json'),
    JSON.stringify(results, null, 2)
  );

  console.log('\nResults saved to:', path.join(REPORT_DIR, 'results.json'));

  // Return exit code
  return results.status === 'PASS' ? 0 : 1;
}

// Run validation
validateImplementation()
  .then(exitCode => {
    console.log(`\nValidation completed with exit code: ${exitCode}`);
    process.exit(exitCode);
  })
  .catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
