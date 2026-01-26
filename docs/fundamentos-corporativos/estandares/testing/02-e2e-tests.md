---
id: e2e-tests
sidebar_position: 2
title: Testing End-to-End (E2E)
description: Estándar para implementar pruebas E2E automatizadas con Playwright y Cypress, validando flujos completos de usuario.
---

# Estándar: Testing End-to-End (E2E)

## 1. Propósito

Definir las mejores prácticas para implementar **pruebas End-to-End (E2E)** automatizadas que validen flujos completos de usuario, garantizando que la aplicación funcione correctamente desde la perspectiva del usuario final.

## 2. Alcance

- Aplicaciones web (SPAs, SSR, full-stack)
- APIs REST con flujos multi-step
- Flujos críticos de negocio (login, checkout, onboarding)
- Testing cross-browser y cross-device
- Integración en CI/CD pipelines

## 3. Principios

### 3.1 Test Pyramid Invertida para E2E

```
         /\
        /  \     ← E2E Tests (10-20% - Flujos críticos)
       /────\
      /      \   ← Integration Tests (30-40%)
     /────────\
    /          \ ← Unit Tests (50-60%)
   /────────────\
```

**Cobertura recomendada**:

- **Unit tests**: 50-60% (rápidos, baratos)
- **Integration tests**: 30-40% (moderados)
- **E2E tests**: 10-20% (lentos, costosos, frágiles)

### 3.2 Solo Flujos Críticos

Priorizar E2E tests para:

- ✅ Login y autenticación
- ✅ Checkout y pagos
- ✅ Registro de usuarios
- ✅ Flujos happy path principales
- ❌ Edge cases (mejor en unit/integration tests)
- ❌ Validaciones simples de formularios

### 3.3 Frameworks Recomendados

| Framework      | Caso de Uso                          | Ventajas                                                 |
| -------------- | ------------------------------------ | -------------------------------------------------------- |
| **Playwright** | Aplicaciones modernas, multi-browser | Auto-wait, debugging, parallelización, TypeScript nativo |
| **Cypress**    | SPAs, desarrollo iterativo           | DX excelente, time-travel, hot reload                    |
| **Selenium**   | Legacy, cross-platform complejo      | Madurez, múltiples lenguajes                             |

**Recomendación**: **Playwright** para nuevos proyectos (mejor rendimiento y mantenibilidad).

## 4. Playwright (Recomendado)

### 4.1 Instalación y Configuración

```bash
# Instalar Playwright
npm init playwright@latest

# Estructura generada
tests/
  ├── example.spec.ts
  └── fixtures/
playwright.config.ts
package.json
```

**playwright.config.ts**:

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // No permitir .only en CI
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html"], ["junit", { outputFile: "test-results/junit.xml" }]],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    // Mobile viewports
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
  ],

  // Servidor local para testing
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### 4.2 Anatomía de un Test E2E

**tests/e2e/auth/login.spec.ts**:

```typescript
import { test, expect } from "@playwright/test";

test.describe("Autenticación de Usuario", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("debe permitir login con credenciales válidas", async ({ page }) => {
    // Arrange
    const email = "usuario@talma.com";
    const password = "Password123!";

    // Act
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.click('[data-testid="login-button"]');

    // Assert
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator('[data-testid="user-profile"]')).toContainText(
      email,
    );
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  test("debe mostrar error con credenciales inválidas", async ({ page }) => {
    await page.fill('[data-testid="email-input"]', "invalido@talma.com");
    await page.fill('[data-testid="password-input"]', "wrongpass");
    await page.click('[data-testid="login-button"]');

    await expect(page.locator('[data-testid="error-message"]')).toContainText(
      "Credenciales inválidas",
    );
    await expect(page).toHaveURL("/login"); // No redirige
  });

  test("debe validar campos requeridos", async ({ page }) => {
    await page.click('[data-testid="login-button"]');

    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });
});
```

### 4.3 Page Object Model (POM)

**pages/LoginPage.ts**:

```typescript
import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('[data-testid="email-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async waitForErrorMessage() {
    await this.errorMessage.waitFor({ state: "visible" });
  }
}
```

**Uso en test**:

```typescript
import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";

test("login con POM", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login("usuario@talma.com", "Password123!");

  await expect(page).toHaveURL("/dashboard");
});
```

### 4.4 Fixtures y Test Helpers

**fixtures/auth.fixture.ts**:

```typescript
import { test as base } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";

type AuthFixtures = {
  loginPage: LoginPage;
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  // Fixture que devuelve página ya autenticada
  authenticatedPage: async ({ page }, use) => {
    // Login automático
    await page.goto("/login");
    await page.fill(
      '[data-testid="email-input"]',
      process.env.TEST_USER_EMAIL!,
    );
    await page.fill(
      '[data-testid="password-input"]',
      process.env.TEST_USER_PASSWORD!,
    );
    await page.click('[data-testid="login-button"]');
    await page.waitForURL("/dashboard");

    await use(page);
  },
});

export { expect } from "@playwright/test";
```

**Uso**:

```typescript
import { test, expect } from "./fixtures/auth.fixture";

test("navegar al perfil requiere autenticación", async ({
  authenticatedPage,
}) => {
  // Ya está autenticado por el fixture
  await authenticatedPage.goto("/profile");
  await expect(
    authenticatedPage.locator('[data-testid="profile-header"]'),
  ).toBeVisible();
});
```

### 4.5 Gestión de Estado y Datos de Prueba

**Seed de datos antes de tests**:

```typescript
import { test as setup } from "@playwright/test";

setup("seed database", async ({ request }) => {
  // Crear datos de prueba vía API
  await request.post("/api/test/seed", {
    data: {
      users: [
        { email: "test@talma.com", role: "admin" },
        { email: "user@talma.com", role: "user" },
      ],
      products: [{ name: "Product 1", price: 100 }],
    },
  });
});
```

**Configurar en playwright.config.ts**:

```typescript
export default defineConfig({
  globalSetup: require.resolve("./global-setup"),
  globalTeardown: require.resolve("./global-teardown"),
});
```

### 4.6 Interceptar Requests/Responses

```typescript
test("mockear respuesta de API", async ({ page }) => {
  // Interceptar y mockear
  await page.route("**/api/users", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        users: [{ id: 1, name: "Mock User" }],
      }),
    });
  });

  await page.goto("/users");
  await expect(page.locator("text=Mock User")).toBeVisible();
});

test("verificar request enviado", async ({ page }) => {
  const requestPromise = page.waitForRequest("**/api/login");

  await page.fill('[data-testid="email-input"]', "test@talma.com");
  await page.click('[data-testid="login-button"]');

  const request = await requestPromise;
  const postData = request.postDataJSON();
  expect(postData.email).toBe("test@talma.com");
});
```

### 4.7 Testing de APIs con Playwright

```typescript
import { test, expect } from "@playwright/test";

test.describe("API Tests", () => {
  test("GET /api/users debe retornar lista", async ({ request }) => {
    const response = await request.get("/api/users");

    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);

    const users = await response.json();
    expect(users.length).toBeGreaterThan(0);
    expect(users[0]).toHaveProperty("id");
    expect(users[0]).toHaveProperty("email");
  });

  test("POST /api/users debe crear usuario", async ({ request }) => {
    const newUser = {
      email: "nuevo@talma.com",
      name: "Nuevo Usuario",
    };

    const response = await request.post("/api/users", {
      data: newUser,
    });

    expect(response.ok()).toBeTruthy();
    const created = await response.json();
    expect(created.email).toBe(newUser.email);
  });
});
```

## 5. Cypress (Alternativa)

### 5.1 Configuración Básica

```bash
npm install --save-dev cypress
npx cypress open
```

**cypress.config.ts**:

```typescript
import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:3000",
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // Plugins
    },
  },
  env: {
    apiUrl: "http://localhost:5000/api",
  },
});
```

### 5.2 Ejemplo de Test

**cypress/e2e/auth/login.cy.ts**:

```typescript
describe("Login Flow", () => {
  beforeEach(() => {
    cy.visit("/login");
  });

  it("debe permitir login exitoso", () => {
    cy.get('[data-testid="email-input"]').type("usuario@talma.com");
    cy.get('[data-testid="password-input"]').type("Password123!");
    cy.get('[data-testid="login-button"]').click();

    cy.url().should("include", "/dashboard");
    cy.get('[data-testid="welcome-message"]').should("be.visible");
  });

  it("debe mostrar error con credenciales inválidas", () => {
    cy.get('[data-testid="email-input"]').type("invalido@talma.com");
    cy.get('[data-testid="password-input"]').type("wrongpass");
    cy.get('[data-testid="login-button"]').click();

    cy.get('[data-testid="error-message"]')
      .should("be.visible")
      .and("contain", "Credenciales inválidas");
  });
});
```

### 5.3 Custom Commands

**cypress/support/commands.ts**:

```typescript
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      seedDatabase(): Chainable<void>;
    }
  }
}

Cypress.Commands.add("login", (email, password) => {
  cy.session([email, password], () => {
    cy.visit("/login");
    cy.get('[data-testid="email-input"]').type(email);
    cy.get('[data-testid="password-input"]').type(password);
    cy.get('[data-testid="login-button"]').click();
    cy.url().should("include", "/dashboard");
  });
});

Cypress.Commands.add("seedDatabase", () => {
  cy.request("POST", `${Cypress.env("apiUrl")}/test/seed`);
});
```

**Uso**:

```typescript
describe("Dashboard", () => {
  beforeEach(() => {
    cy.seedDatabase();
    cy.login("usuario@talma.com", "Password123!");
    cy.visit("/dashboard");
  });

  it("debe mostrar widgets", () => {
    cy.get('[data-testid="widget-sales"]').should("be.visible");
  });
});
```

## 6. Mejores Prácticas Generales

### 6.1 Selectores Confiables

**Prioridad de selectores**:

```typescript
// ✅ MEJOR: data-testid (estable, semántico)
await page.locator('[data-testid="submit-button"]').click();

// ✅ BIEN: role + nombre accesible (semántico)
await page.getByRole("button", { name: "Enviar" }).click();

// ⚠️ ACEPTABLE: por texto (puede cambiar con i18n)
await page.getByText("Enviar").click();

// ❌ EVITAR: clases CSS (frágiles)
await page.locator(".btn-primary").click();

// ❌ EVITAR: XPath complejos (no mantenibles)
await page.locator('//div[@class="container"]//button[1]').click();
```

**Agregar data-testid en componentes**:

```tsx
// React
<button data-testid="login-button" onClick={handleLogin}>
  Iniciar Sesión
</button>

// Angular
<button data-testid="login-button" (click)="handleLogin()">
  Iniciar Sesión
</button>
```

### 6.2 Esperas Explícitas (Auto-Wait)

```typescript
// ✅ Playwright auto-wait (mejor práctica)
await page.locator('[data-testid="result"]').waitFor({ state: "visible" });
await page.click('[data-testid="button"]'); // Auto-espera a que sea clickable

// ✅ Esperar por estado específico
await page.locator('[data-testid="spinner"]').waitFor({ state: "hidden" });

// ❌ EVITAR: sleeps arbitrarios
await page.waitForTimeout(2000); // Frágil y lento
```

### 6.3 Manejo de Flakiness

```typescript
// ✅ Configurar retries
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
});

// ✅ Soft assertions (continuar después de fallo)
await expect.soft(page.locator(".title")).toHaveText("Expected");
await expect.soft(page.locator(".subtitle")).toBeVisible();

// ✅ Auto-retry de acciones
await page.locator('[data-testid="button"]').click({ timeout: 10000 });
```

### 6.4 Paralelización y Performance

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined, // Limitar en CI
});

// Ejecutar tests específicos
npx playwright test --grep @smoke
npx playwright test --grep-invert @slow
```

**Tagging de tests**:

```typescript
test("login @smoke @critical", async ({ page }) => {
  // Test crítico para smoke testing
});

test("export report @slow", async ({ page }) => {
  // Test lento, excluir de smoke
});
```

### 6.5 Debugging

```typescript
// Pausar ejecución
await page.pause();

// Debug con inspector
PWDEBUG=1 npx playwright test

// Verbose logging
DEBUG=pw:api npx playwright test

// Trace viewer (post-mortem)
npx playwright show-trace trace.zip
```

## 7. Integración con CI/CD

### 7.1 GitHub Actions

**.github/workflows/e2e.yml**:

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps ${{ matrix.browser }}

      - name: Run E2E tests
        run: npx playwright test --project=${{ matrix.browser }}
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/
          retention-days: 7
```

### 7.2 GitLab CI

**.gitlab-ci.yml**:

```yaml
e2e-tests:
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  stage: test
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 1 week
  only:
    - merge_requests
    - main
```

## 8. Estructura de Proyecto

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   └── logout.spec.ts
│   ├── checkout/
│   │   ├── cart.spec.ts
│   │   └── payment.spec.ts
│   └── admin/
│       └── users.spec.ts
├── fixtures/
│   ├── auth.fixture.ts
│   └── data.fixture.ts
├── pages/
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   └── CheckoutPage.ts
├── helpers/
│   ├── api.helper.ts
│   └── db.helper.ts
└── global-setup.ts
playwright.config.ts
```

## 9. Métricas y Reportes

### 9.1 Playwright HTML Report

```bash
npx playwright test --reporter=html
npx playwright show-report
```

### 9.2 Custom Reporter

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: [
    ["html"],
    ["junit", { outputFile: "results.xml" }],
    ["json", { outputFile: "results.json" }],
    ["./custom-reporter.ts"],
  ],
});
```

## 10. NO Hacer

❌ **NO** testear todo con E2E (usar pirámide de tests)
❌ **NO** usar selectores frágiles (CSS classes, XPath complejos)
❌ **NO** hacer sleeps/waits arbitrarios (`waitForTimeout`)
❌ **NO** tener tests interdependientes (cada test debe ser independiente)
❌ **NO** compartir estado entre tests
❌ **NO** ignorar flakiness (investigar y resolver)
❌ **NO** correr E2E en cada commit (solo en CI/CD para PRs y main)

## 11. Referencias

### Documentación Oficial

- [Playwright Documentation](https://playwright.dev/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles)

### Lineamientos Relacionados

- [Lineamiento Arq. 07: Calidad y Testing](../../lineamientos/arquitectura/07-calidad-testing.md)
- [Lineamiento Dev. 03: Testing](../../lineamientos/desarrollo/03-testing.md)

### Otros Estándares

- [Unit & Integration Tests](./01-unit-integration-tests.md) - Testing unitario e integración
- [C# / .NET](../codigo/01-csharp-dotnet.md) - Clean Code y testing en .NET
- [TypeScript](../codigo/02-typescript.md) - Clean Code TypeScript
