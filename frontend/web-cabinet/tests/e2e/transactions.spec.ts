import { test, expect } from '@playwright/test';

test.describe('Transactions Page', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[id="username"]', 'testuser');
    await page.fill('input[id="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Navigate to transactions
    await page.click('text=Транзакції');
    await page.waitForURL('/transactions');
  });

  test('should display transactions page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Транзакції');
    await expect(page.locator('text=Управління транзакціями')).toBeVisible();
  });

  test('should display create transaction button', async ({ page }) => {
    await expect(page.locator('button').filter({ hasText: 'Додати транзакцію' })).toBeVisible();
  });

  test('should display transaction filters', async ({ page }) => {
    await expect(page.locator('text=Фільтри')).toBeVisible();
    await expect(page.locator('select[name="type"]')).toBeVisible();
    await expect(page.locator('select[name="category"]')).toBeVisible();
    await expect(page.locator('input[name="date_from"]')).toBeVisible();
    await expect(page.locator('input[name="date_to"]')).toBeVisible();
  });

  test('should display transaction table', async ({ page }) => {
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Дата' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Опис' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Категорія' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Сума' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Тип' })).toBeVisible();
  });

  test('should open create transaction modal', async ({ page }) => {
    await page.click('button').filter({ hasText: 'Додати транзакцію' });
    await expect(page.locator('text=Створити транзакцію')).toBeVisible();
    await expect(page.locator('input[name="amount"]')).toBeVisible();
    await expect(page.locator('input[name="description"]')).toBeVisible();
    await expect(page.locator('select[name="type"]')).toBeVisible();
    await expect(page.locator('select[name="category"]')).toBeVisible();
  });

  test('should create new transaction', async ({ page }) => {
    // Open create modal
    await page.click('button').filter({ hasText: 'Додати транзакцію' });
    
    // Fill form
    await page.fill('input[name="amount"]', '100.00');
    await page.fill('input[name="description"]', 'Test Transaction');
    await page.selectOption('select[name="type"]', 'expense');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should close modal and show success
    await expect(page.locator('text=Створити транзакцію')).not.toBeVisible();
  });

  test('should filter transactions by type', async ({ page }) => {
    await page.selectOption('select[name="type"]', 'expense');
    await page.click('button').filter({ hasText: 'Застосувати фільтри' });
    
    // Should show filtered results
    await expect(page.locator('table')).toBeVisible();
  });

  test('should search transactions', async ({ page }) => {
    await page.fill('input[name="search"]', 'test');
    await page.click('button').filter({ hasText: 'Пошук' });
    
    // Should show search results
    await expect(page.locator('table')).toBeVisible();
  });

  test('should export transactions', async ({ page }) => {
    await expect(page.locator('button').filter({ hasText: 'Експорт CSV' })).toBeVisible();
    await expect(page.locator('button').filter({ hasText: 'Експорт Excel' })).toBeVisible();
  });

  test('should display transaction statistics', async ({ page }) => {
    await expect(page.locator('text=Статистика')).toBeVisible();
    await expect(page.locator('text=Загальний дохід')).toBeVisible();
    await expect(page.locator('text=Загальні витрати')).toBeVisible();
    await expect(page.locator('text=Баланс')).toBeVisible();
  });
});
