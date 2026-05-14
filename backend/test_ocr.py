import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import easyocr
import PIL.Image
import io

# Configuration
TEST_AUTHOR_URL = "https://sbrmedia.com/authors/bella-di-corte/"
TEST_AUTHOR_NAME = "Bella Di Corte"
TEMP_IMG_DIR = "backend/scratch/ocr_temp"

if not os.path.exists(TEMP_IMG_DIR):
    os.makedirs(TEMP_IMG_DIR)

async def capture_and_read_books(page):
    print(f"[OCR] Scanning {TEST_AUTHOR_NAME} books...", flush=True)
    await page.goto(TEST_AUTHOR_URL, wait_until="networkidle")
    
    # Initialize EasyOCR Reader (English)
    print("  Initializing OCR engine...", flush=True)
    reader = easyocr.Reader(['en'], gpu=False) # GPU False for compatibility
    
    # Find all images in the carousel area
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await asyncio.sleep(2)
    
    # Select all images that look like book covers
    images = await page.query_selector_all("img")
    extracted_titles = set()
    
    # For testing, we'll click the next button to ensure we see everything
    next_btn = await page.query_selector(".elementor-swiper-button-next")
    
    for i in range(10): # Click up to 10 times
        print(f"  Processing Carousel Slide {i+1}...", flush=True)
        
        # Re-query images on current slide
        visible_images = await page.query_selector_all("img")
        
        for idx, img in enumerate(visible_images):
            if await img.is_visible():
                box = await img.bounding_box()
                if box and box['width'] > 50 and box['height'] > 50:
                    # Capture a screenshot of just this image
                    img_path = os.path.join(TEMP_IMG_DIR, f"book_{i}_{idx}.png")
                    await img.screenshot(path=img_path)
                    
                    # Read text from the screenshot
                    print(f"    Reading cover {idx}...", flush=True)
                    results = reader.readtext(img_path)
                    
                    # Combine found text chunks into a potential title
                    cover_text = " ".join([res[1] for res in results if res[2] > 0.3])
                    if len(cover_text) > 3:
                        # Simple cleanup - remove author name from title if found
                        clean_title = cover_text.replace(TEST_AUTHOR_NAME, "").strip()
                        if clean_title:
                            print(f"      -> Visually Detected: {clean_title}")
                            extracted_titles.add(clean_title)
        
        if next_btn and await next_btn.is_visible():
            await next_btn.click()
            await asyncio.sleep(1.5)
        else:
            break
            
    return list(extracted_titles)

async def run_ocr_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Visual Extraction
        titles = await capture_and_read_books(page)
        
        print(f"\n[Summary] Successfully extracted {len(titles)} titles via OCR:")
        for t in titles:
            print(f"  - {t}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ocr_test())
