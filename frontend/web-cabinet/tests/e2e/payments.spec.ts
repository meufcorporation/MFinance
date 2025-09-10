import { test, expect } from '@playwright/test';

test.describe('Payments Page', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[id="username"]', 'testuser');
    await page.fill('input[id="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Navigate to payments
    await page.click('text=Платежі');
    await page.waitForURL('/payments');
  });

  test('should display payments page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Платежі');
    await expect(page.locator('text=Управління платежами')).toBeVisible();
  });

  test('should display payment tabs', async ({ page }) => {
    await expect(page.locator('text=Способи оплати')).toBeVisible();
    await expect(page.locator('text=Платежі')).toBeVisible();
    await expect(page.locator('text=Розклади платежів')).toBeVisible();
    await expect(page.locator('text=Шаблони платежів')).toBeVisible();
  });

  test('should display add payment method button', async ({ page }) => {
    await page.click('text=Способи оплати');
    await expect(page.locator('button').filter({ hasText: 'Додати спосіб оплати' })).toBeVisible();
  });

  test('should open add payment method modal', async ({ page }) => {
    await page.click('text=Способи оплати');
    await page.click('button').filter({ hasText: 'Додати спосіб оплати' });
    
    await expect(page.locator('text=Додати спосіб оплати')).toBeVisible();
    await expect(page.locator('select[name="method_type"]')).toBeVisible();
    await expect(page.locator('select[name="provider"]')).toBeVisible();
  });

  test('should add new payment method', async ({ page }) => {
    await page.click('text=Способи оплати');
    await page.click('button').filter({ hasText: 'Додати спосіб оплати' });
    
    // Fill form
    await page.selectOption('select[name="method_type"]', 'card');
    await page.fill('input[name="card_holder"]', 'Test User');
    await page.fill('input[name="card_number"]', '1234567890123456');
    await page.fill('input[name="expiry_date"]', '12/25');
    await page.fill('input[name="cvv"]', '123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should close modal
    await expect(page.locator('text=Додати спосіб оплати')).not.toBeVisible();
  });

  test('should display payments list', async ({ page }) => {
    await page.click('text=Платежі');
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'ID' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Сума' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Тип' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Статус' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Дата' })).toBeVisible();
  });

  test('should create new payment', async ({ page }) => {
    await page.click('text=Платежі');
    await page.click('button').filter({ hasText: 'Створити платіж' });
    
    await expect(page.locator('text=Створити платіж')).toBeVisible();
    await expect(page.locator('input[name="amount"]')).toBeVisible();
    await expect(page.locator('select[name="payment_type"]')).toBeVisible();
    await expect(page.locator('select[name="payment_method"]')).toBeVisible();
  });

  test('should display payment schedules', async ({ page }) => {
    await page.click('text=Розклади платежів');
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Назва' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Частота' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Сума' })).toBeVisible();
    await expect(page.locator('th').filter({ hasText: 'Статус' })).toBeVisible();
  });

  test('should create payment schedule', async ({ page }) => {
    await page.click('text=Розклади платежів');
    await page.click('button').filter({ hasText: 'Створити розклад' });
    
    await expect(page.locator('text=Створити розклад платежів')).toBeVisible();
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('select[name="frequency"]')).toBeVisible();
    await expect(page.locator('input[name="amount"]')).toBeVisible();
  });

  test('should display payment templates', async ({ page }) => {
    await page.click('text=Шаблони платежів');
    await expect(page.locator('text=Шаблони платежів')).toBeVisible();
    await expect(page.locator('button').filter({ hasText: 'Створити шаблон' })).toBeVisible();
  });

  test('should create payment template', async ({ page }) => {
    await page.click('text=Шаблони платежів');
    await page.click('button').filter({ hasText: 'Створити шаблон' });
    
    await expect(page.locator('text=Створити шаблон платежу')).toBeVisible();
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('input[name="amount"]')).toBeVisible();
    await expect(page.locator('select[name="payment_type"]')).toBeVisible();
  });

  test('should display payment statistics', async ({ page }) => {
    await expect(page.locator('text=Статистика платежів')).toBeVisible();
    await expect(page.locator('text=Загальна сума')).toBeVisible();
    await expect(page.locator('text=Успішні платежі')).toBeVisible();
    await expect(page.locator('text=Неуспішні платежі')).toBeVisible();
  });
});
