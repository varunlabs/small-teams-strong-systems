# PDF generation script using pyppeteer instead of WeasyPrint
import asyncio
import sys
import os
from pyppeteer import launch

async def html_to_pdf(html_file, pdf_file):
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()

    # Set viewport for better PDF output
    await page.setViewport({'width': 800, 'height': 600})

    # Load HTML file
    await page.goto(f'file://{os.path.abspath(html_file)}')

    # Generate PDF
    await page.pdf({
        'path': pdf_file,
        'format': 'A5',
        'margin': {
            'top': '25mm',
            'bottom': '25mm',
            'left': '22mm',
            'right': '22mm'
        }
    })

    await browser.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python html_to_pdf.py <html_file> <pdf_file>")
        sys.exit(1)

    html_file = sys.argv[1]
    pdf_file = sys.argv[2]

    asyncio.run(html_to_pdf(html_file, pdf_file))