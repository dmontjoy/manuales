import asyncio
from playwright.async_api import async_playwright
import os
import time

async def main():
    os.makedirs('manual-assets', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a standard 1280x720 or 1920x1080 resolution
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to login...")
        await page.goto("http://localhost:4200/auth/login/metro2")
        
        # Clear storage and reload for clean login
        await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        
        # 1. Login screenshot
        print("Capturing login...")
        await page.screenshot(path="manual-assets/01-login.png", full_page=True)

        # Fill credentials
        print("Logging in...")
        # We need to find the username and password inputs.
        # usually input[type="text"] or [name="username"] etc. Let's try to type.
        # If we don't know the selectors, we can look for placeholders or input types.
        await page.fill('input[type="text"], input[formcontrolname="username"], input[name="username"], input[placeholder*="Usuario"]', 'admin', timeout=2000)
        await page.fill('input[type="password"]', 'Delfos2017.')
        
        # Click login button
        await page.click('button[type="submit"], button:has-text("Iniciar Sesión"), button:has-text("Ingresar")')
        
        # 2. Inicio
        print("Waiting for inicio...")
        await page.wait_for_url("**/pages/inicio", timeout=15000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2) # Give it some time to render charts
        print("Capturing inicio...")
        await page.screenshot(path="manual-assets/02-inicio.png", full_page=True)
        
        routes = [
            ("03-stakeholders-lista.png", "/pages/gestion/stakeholder"),
            ("05-interacciones.png", "/pages/gestion/interaccion"),
            ("06-reclamos.png", "/pages/gestion/reclamo"),
            ("07-solicitudes.png", "/pages/gestion/solicitud"),
            ("08-compromisos.png", "/pages/gestion/commitment"),
            ("09-reporte-interaccion.png", "/pages/reporte/reporte-interaccion"),
            ("10-delfos-ia.png", "/pages/delfos-ia"),
            ("11-configuracion-tag.png", "/pages/setup/tag"),
        ]

        # For stakeholder Ficha, we need to click on a stakeholder first, or guess an ID
        # Let's go to list, click the first row
        
        for filename, route in routes:
            print(f"Navigating to {route}...")
            await page.goto(f"http://localhost:4200{route}")
            await page.wait_for_load_state("networkidle")
            # Wait for any spinner to disappear. A rough heuristic: wait 2 seconds after network idle.
            await asyncio.sleep(2)
            print(f"Capturing {filename}...")
            await page.screenshot(path=f"manual-assets/{filename}", full_page=True)
            
            # If we are on stakeholders list, let's capture a Ficha
            if route == "/pages/gestion/stakeholder":
                print("Trying to open Ficha de stakeholder...")
                # Try clicking a row or an action button to open ficha
                # Typically it's a table row td or a button with icon "eye" or "edit" or just text
                try:
                    # Let's just click the first link/button in the first table row
                    await page.click("table tbody tr:first-child", timeout=3000)
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(2)
                    await page.screenshot(path="manual-assets/04-stakeholder-ficha.png", full_page=True)
                    
                    # We can also capture tabs if they are visible
                    # Then we navigate back
                    await page.goto(f"http://localhost:4200{route}")
                    await page.wait_for_load_state("networkidle")
                except Exception as e:
                    print("Could not open ficha directly:", e)

            # If we are on a list, try to open the Export options modal
            if route == "/pages/gestion/reclamo":
                print("Trying to open Export modal...")
                try:
                    await page.click('button:has-text("Exportar"), button:has-text("Descargar"), mat-icon:has-text("download")', timeout=2000)
                    await asyncio.sleep(1)
                    await page.screenshot(path="manual-assets/12-opciones-descarga.png")
                    # Close modal (ESC key)
                    await page.keyboard.press("Escape")
                except Exception as e:
                    print("Could not open export modal:", e)

        print("Done capturing!")
        await browser.close()

asyncio.run(main())
