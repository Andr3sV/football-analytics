#!/usr/bin/env python3
"""
Debug solidarity form structure
"""
import requests
import cloudscraper
from bs4 import BeautifulSoup
import json

def debug_solidarity_form():
    # Create session
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'mobile': False
        }
    )
    
    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        print("🌐 Fetching solidarity calculator page...")
        response = scraper.get('https://www.transfermarkt.com/solidarityFeeCalculator/index')
        
        if response.status_code != 200:
            print(f"❌ Failed to load page: {response.status_code}")
            return
        
        print(f"✅ Page loaded successfully")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        print(f"\n📋 Found {len(forms)} forms:")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i}:")
            print(f"  Action: {form.get('action', 'No action')}")
            print(f"  Method: {form.get('method', 'No method')}")
            print(f"  Class: {form.get('class', 'No class')}")
            print(f"  ID: {form.get('id', 'No ID')}")
            
            # Find all inputs in this form
            inputs = form.find_all('input')
            print(f"  Inputs ({len(inputs)}):")
            for inp in inputs:
                inp_type = inp.get('type', 'text')
                inp_name = inp.get('name', 'No name')
                inp_id = inp.get('id', 'No ID')
                inp_placeholder = inp.get('placeholder', 'No placeholder')
                print(f"    - Type: {inp_type}, Name: {inp_name}, ID: {inp_id}, Placeholder: {inp_placeholder}")
            
            # Find all buttons in this form
            buttons = form.find_all('button')
            print(f"  Buttons ({len(buttons)}):")
            for btn in buttons:
                btn_type = btn.get('type', 'button')
                btn_text = btn.get_text(strip=True)
                btn_class = btn.get('class', 'No class')
                print(f"    - Type: {btn_type}, Text: '{btn_text}', Class: {btn_class}")
        
        # Look for any JavaScript that might be handling the form
        scripts = soup.find_all('script')
        print(f"\n🔍 Found {len(scripts)} script tags")
        
        for i, script in enumerate(scripts):
            if script.string and ('solidarity' in script.string.lower() or 'player' in script.string.lower()):
                print(f"\nScript {i} (relevant content):")
                # Show first 500 characters
                content = script.string[:500]
                print(content)
                if len(script.string) > 500:
                    print("... (truncated)")
        
        # Look for any data attributes or JSON data
        print(f"\n🔍 Looking for data attributes...")
        elements_with_data = soup.find_all(attrs=lambda x: x and isinstance(x, dict) and any(k.startswith('data-') for k in x.keys()))
        for elem in elements_with_data[:5]:  # Show first 5
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            print(f"  Element: {elem.name}, Data attrs: {data_attrs}")
        
        # Save HTML for manual inspection
        with open('solidarity_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n💾 Saved page HTML to solidarity_page.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_solidarity_form()
