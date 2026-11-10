from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w in [("table", 2400), ("check", 2000)]:
        pg = b.new_page(viewport={"width": w, "height": 800})
        pg.goto("file://" + os.path.abspath(f"out/{name}.html"))
        pg.screenshot(path=f"out/{name}.png", full_page=True)
    b.close()
