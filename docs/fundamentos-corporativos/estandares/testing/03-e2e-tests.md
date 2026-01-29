---
id: e2e-tests
sidebar_position: 3
title: Testing End-to-End (E2E)
description: Estándar para implementar pruebas E2E automatizadas con Playwright y Cypress, validando flujos completos de usuario.
---

# Estándar Técnico — Testing End-to-End (E2E)

---

## 1. Propósito
Validar flujos críticos de usuario completos (login, checkout, onboarding) usando Playwright (recomendado), ejecución multi-browser (Chromium, Firefox, Webkit), data-testid selectors y retry logic automático.

---

## 2. Alcance

**Aplica a:**
- Aplicaciones web (SPAs, SSR)
- Flujos críticos (login, checkout, registro)
- Testing cross-browser (Chrome, Firefox, Safari)
- APIs con flujos multi-step

**No aplica a:**
- Validaciones simples (usar unit tests)
- Lógica de negocio aislada (usar unit tests)
- Tests de performance (usar benchmarks)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **E2E Framework** | Playwright | 1.40+ | Recomendado (multi-browser) |
| **Alternativa** | Cypress | 13.0+ | SPAs, DX excelente |
| **CI/CD** | GitHub Actions | - | Playwright + containers |
| **Reporters** | HTML / JUnit | - | Reporting tests |
| **Screenshots** | Playwright | - | Auto-captura en fallas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Playwright (recomendado) o Cypress
- [ ] Cobertura 10-20% (solo flujos críticos)
- [ ] Selectors con `data-testid` (NO CSS classes)
- [ ] Retry logic habilitado (2 retries en CI)
- [ ] Screenshots/videos en fallas
- [ ] Multi-browser (Chromium, Firefox, Webkit)
- [ ] Ejecución paralela cuando sea posible
- [ ] Environment variables en `.env.e2e`
- [ ] Naming: `describe('Feature')` + `test('action_scenario_result')`
- [ ] Cleanup después de cada test (logout, clear cookies)
- [ ] NO sleeps/waits fijos (usar auto-waiting)
- [ ] Integración en CI/CD (GitHub Actions)

---

## 5. Prohibiciones

- ❌ Selectors CSS frágiles (`.btn-primary`)
- ❌ Sleeps fijos (`page.waitForTimeout(5000)`)
- ❌ Tests E2E para validaciones simples
- ❌ Hardcoded URLs (usar baseURL config)
- ❌ Tests interdependientes (orden de ejecución)
- ❌ >20% cobertura E2E (usar unit/integration tests)
- ❌ Secrets en código (usar env vars)

---

## 6. Configuración Mínima

### Playwright (Recomendado)
```bash
npm init playwright@latest
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['junit', { outputFile: 'test-results/junit.xml' }]],
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

```typescript
// tests/e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Autenticación', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('debe permitir login con credenciales válidas', async ({ page }) => {
    // Arrange
    const email = 'usuario@talma.com';
    const password = 'Password123!';

    // Act
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.click('[data-testid="login-button"]');

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByTestId('user-name')).toContainText('Usuario');
  });

  test('debe mostrar error con credenciales inválidas', async ({ page }) => {
    // Act
    await page.fill('[data-testid="email-input"]', 'invalido@talma.com');
    await page.fill('[data-testid="password-input"]', 'wrong');
    await page.click('[data-testid="login-button"]');

    // Assert
    await expect(page.getByTestId('error-message')).toBeVisible();
    await expect(page.getByTestId('error-message')).toContainText('Credenciales inválidas');
  });
});
```

---

## 7. Validación

```bash
# Ejecutar E2E tests
npx playwright test

# Ejecutar en headed mode (debug)
npx playwright test --headed

# UI mode (interactivo)
npx playwright test --ui

# Ejecutar en browser específico
npx playwright test --project=chromium

# Ver reporte HTML
npx playwright show-report
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Cobertura E2E | 10-20% | Solo flujos críticos |
| Selectors data-testid | 100% | Code review |
| Retry habilitado | CI = 2 retries | playwright.config.ts |
| Multi-browser | 3 browsers | Chromium, Firefox, Webkit |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Unit Tests](01-unit-tests.md)
- [Integration Tests](02-integration-tests.md)
- [Playwright Documentation](https://playwright.dev/)
- [Cypress Documentation](https://www.cypress.io/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
