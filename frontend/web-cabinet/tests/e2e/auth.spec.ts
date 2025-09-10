import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/MFinance/);
    await expect(page.locator('h1')).toContainText('Вхід в MFinance');
    await expect(page.locator('input[id="username"]')).toBeVisible();
    await expect(page.locator('input[id="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText('Увійти');
  });

  test('should show Keycloak login button', async ({ page }) => {
    await expect(page.locator('button').filter({ hasText: 'Увійти через Keycloak' })).toBeVisible();
  });

  test('should display test account information', async ({ page }) => {
    await expect(page.locator('text=Тестові акаунти')).toBeVisible();
    await expect(page.locator('text=testuser / testpass123')).toBeVisible();
    await expect(page.locator('text=admin / admin123')).toBeVisible();
    await expect(page.locator('text=test@mfinance.com / test123')).toBeVisible();
  });

  test('should handle form validation', async ({ page }) => {
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('input[id="username"]:invalid')).toBeVisible();
    await expect(page.locator('input[id="password"]:invalid')).toBeVisible();
  });

  test('should display form elements correctly', async ({ page }) => {
    // Check username field
    await expect(page.locator('input[id="username"]')).toBeVisible();
    await expect(page.locator('input[id="username"]')).toHaveAttribute('type', 'text');
    
    // Check password field
    await expect(page.locator('input[id="password"]')).toBeVisible();
    await expect(page.locator('input[id="password"]')).toHaveAttribute('type', 'password');
    
    // Check submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeEnabled();
  });

  test('should have proper form structure', async ({ page }) => {
    // Check form exists
    await expect(page.locator('form')).toBeVisible();
    
    // Check form has proper method
    await expect(page.locator('form')).toHaveAttribute('method', 'post');
    
    // Check form has proper action
    await expect(page.locator('form')).toHaveAttribute('action', '/api/auth/signin/credentials');
  });
});
