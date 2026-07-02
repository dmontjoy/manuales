import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto("http://localhost:4200/auth/login/metro2")
        await page.fill('input[type="text"], input[formcontrolname="username"], input[name="username"], input[placeholder*="Usuario"]', 'admin')
        await page.fill('input[type="password"]', 'Delfos2017.')
        await page.click('button[type="submit"], button:has-text("Iniciar Sesión"), button:has-text("Ingresar")')
        
        await page.wait_for_url("**/pages/inicio", timeout=15000)
        
        await page.goto("http://localhost:4200/pages/gestion/reclamo")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        try:
            # force=True bypasses visibility checks
            await page.click('button[ng-reflect-message="Opciones de Descarga"], button[mattooltip*="escarg"], button[mattooltip*="xport"], button:has-text("Exportar"), button:has-text("Descargar")', force=True, timeout=3000)
            await asyncio.sleep(2)
            await page.screenshot(path="manual-assets/12-opciones-descarga.png")
            print("Captured export modal")
        except Exception as e:
            print("Still could not open export modal:", e)

        await browser.close()

asyncio.run(main())
