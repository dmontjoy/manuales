import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Logging in again...")
        await page.goto("http://localhost:4200/auth/login/metro2")
        await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        
        await page.fill('input[type="text"], input[formcontrolname="username"], input[name="username"], input[placeholder*="Usuario"]', 'admin')
        await page.fill('input[type="password"]', 'Delfos2017.')
        await page.click('button[type="submit"], button:has-text("Iniciar Sesión"), button:has-text("Ingresar")')
        
        await page.wait_for_url("**/pages/inicio", timeout=15000)
        
        # Try capturing Ficha
        print("Capturing Ficha...")
        for i in [1, 2, 3, 4, 5]:
            print(f"Trying ID {i}...")
            await page.goto(f"http://localhost:4200/pages/gestion/stakeholder/{i}/ficha")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            # If it redirects to list, it means invalid ID, but if it stays, we capture
            if "ficha" in page.url:
                await page.screenshot(path="manual-assets/04-stakeholder-ficha.png", full_page=True)
                print(f"Captured Ficha for ID {i}")
                break
        
        # Try capturing Export Modal
        print("Capturing Export modal...")
        await page.goto("http://localhost:4200/pages/gestion/reclamo")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        try:
            # Broadest possible selectors for the download button
            await page.click('button[mattooltip*="escarg"], button[mattooltip*="xport"], button:has-text("Exportar"), button:has-text("Descargar"), button:has(.fa-download), button:has(mat-icon:has-text("download")), button:has(mat-icon:has-text("get_app")), button:has(mat-icon:has-text("cloud_download"))', timeout=3000)
            await asyncio.sleep(1)
            await page.screenshot(path="manual-assets/12-opciones-descarga.png")
            print("Captured export modal")
        except Exception as e:
            print("Could not open export modal again:", e)

        await browser.close()

asyncio.run(main())
