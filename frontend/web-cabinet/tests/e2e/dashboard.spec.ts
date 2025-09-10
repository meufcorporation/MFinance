import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[id="username"]', 'testuser');
    await page.fill('input[id="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display dashboard page', async ({ page }) => {
    await expect(page).toHaveTitle(/MFinance/);
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('text=Фінансовий дашборд')).toBeVisible();
  });

  test('should display navigation menu', async ({ page }) => {
    const navItems = [
      'Dashboard',
      'Транзакції',
      'ФОП',
      'Платежі',
      'Бюджети',
      'Звіти',
      'Сповіщення',
      'Профіль'
    ];

    for (const item of navItems) {
      await expect(page.locator(`text=${item}`)).toBeVisible();
    }
  });

  test('should display financial summary cards', async ({ page }) => {
    await expect(page.locator('text=Загальний баланс')).toBeVisible();
    await expect(page.locator('text=Доходи цього місяця')).toBeVisible();
    await expect(page.locator('text=Витрати цього місяця')).toBeVisible();
    await expect(page.locator('text=Останні транзакції')).toBeVisible();
  });

  test('should display recent transactions table', async ({ page }) => {
    await expect(page.locator('text=Останні транзакції')).toBeVisible();
    await expect(page.locator('table')).toBeVisible();
  });

  test('should display upcoming tax deadlines', async ({ page }) => {
    await expect(page.locator('text=Найближчі дедлайни')).toBeVisible();
  });

  test('should navigate to different pages from navigation', async ({ page }) => {
    // Test navigation to Transactions
    await page.click('text=Транзакції');
    await expect(page).toHaveURL('/transactions');
    await expect(page.locator('h1')).toContainText('Транзакції');

    // Test navigation to FOP
    await page.click('text=ФОП');
    await expect(page).toHaveURL('/fop');
    await expect(page.locator('h1')).toContainText('ФОП');

    // Test navigation to Payments
    await page.click('text=Платежі');
    await expect(page).toHaveURL('/payments');
    await expect(page.locator('h1')).toContainText('Платежі');

    // Test navigation to Budgets
    await page.click('text=Бюджети');
    await expect(page).toHaveURL('/budgets');
    await expect(page.locator('h1')).toContainText('Бюджети');

    // Test navigation to Reports
    await page.click('text=Звіти');
    await expect(page).toHaveURL('/reports');
    await expect(page.locator('h1')).toContainText('Звіти');
  });

  test('should display user information in header', async ({ page }) => {
    await expect(page.locator('text=Привіт, testuser!')).toBeVisible();
    await expect(page.locator('button').filter({ hasText: 'Вийти' })).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    await page.click('button').filter({ hasText: 'Вийти' });
    await expect(page).toHaveURL('/login');
    await expect(page.locator('h1')).toContainText('Вхід в MFinance');
  });
});
