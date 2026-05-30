import {test, expect} from "@playwright/test";

const goUrl = ("https://demo.playwright.dev/todomvc/");
test ("Automation form", async ({page})=>{
    await page.goto(goUrl);

    const todoInput = page.getByPlaceholder("What needs to be done?");
    await todoInput.fill("Buy auto");
    await todoInput.press("Enter");
    await todoInput.fill("No buy auto with automoto");
    await todoInput.press("Enter");
    await page.waitForTimeout(3000);

    const firstTodo = page.getByTestId('todo-item').nth(0);
    await firstTodo.getByRole('checkbox').click();
    await page.waitForTimeout(1000);

    const secondTodo = page.getByTestId('todo-item').nth(1);
    await expect(secondTodo).not.toHaveClass(/completed/);
    await expect(firstTodo).toHaveClass(/completed/);
});

test.only ("Handling form", async ({page}) =>{
    await page.goto(goUrl);
    const placeHolder = page.getByPlaceholder("What needs to be done?");
    await placeHolder.fill("Buy auto");
    await placeHolder.press("Enter");

    const checkbox = page.locator('.toggle')
    await checkbox.click();
    await page.waitForTimeout(1000);
});