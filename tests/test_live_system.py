import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    s = requests.Session()

    # 1. Guest Home Page
    r1 = s.get(f"{BASE_URL}/")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
    # Verify guest nav does not have Find Tailors
    nav_links_block = r1.text.split('class="nav-links"')[1].split('</div>')[0]
    assert "Find Tailors" not in nav_links_block, "Find Tailors found in guest navbar!"
    assert "Get Started" in r1.text
    assert "Sign in" in r1.text
    print("PASS 1: Guest homepage loaded without 'Find Tailors' in navbar.")

    # 2. Guest access to /customer/tailors should redirect to login
    r2 = s.get(f"{BASE_URL}/customer/tailors", allow_redirects=False)
    assert r2.status_code == 302, f"Expected 302 redirect for guest, got {r2.status_code}"
    assert "/auth/login" in r2.headers["Location"], f"Expected redirect to login, got {r2.headers['Location']}"
    print("PASS 2: Guest access to /customer/tailors correctly redirects to /auth/login.")

    # 3. 3D Floating Login Page
    r3 = s.get(f"{BASE_URL}/auth/login")
    assert r3.status_code == 200
    assert "auth-3d-page" in r3.text
    assert "fashion-object" in r3.text
    assert "chip-measurements" in r3.text
    # Verify Quick Demo Login was removed as requested
    assert "demoCustomerBtn" not in r3.text, "Quick demo login should be removed"
    print("PASS 3: 3D Floating Login page loaded cleanly without quick demo buttons.")

    # 4. Login as Customer (Arjun)
    r4 = s.post(f"{BASE_URL}/auth/login", data={
        "email": "arjun@example.com",
        "password": "password123"
    }, allow_redirects=True)
    assert r4.status_code == 200
    print("PASS 4: Customer login succeeded.")

    # 5. Customer Dashboard with Multiple 3D Designs
    r5 = s.get(f"{BASE_URL}/customer/dashboard")
    assert r5.status_code == 200
    assert "dashboard-3d-showcase" in r5.text
    assert "design-suit" in r5.text
    assert "design-machine" in r5.text
    assert "design-shears" in r5.text
    assert "design-fabric" in r5.text
    assert "design-switch-btn" in r5.text
    print("PASS 5: Customer dashboard loaded with 4 switchable 3D designs (Suit, Machine, Shears, Fabric).")

    # 6. Customer Tailors Discovery with Live Tamil Nadu Map & Specialty Filters
    r6 = s.get(f"{BASE_URL}/customer/tailors")
    assert r6.status_code == 200
    assert "tnTailorMap" in r6.text
    assert "districtPillBar" in r6.text
    assert "specialtyPillBar" in r6.text
    assert "tailorsData" in r6.text
    assert "locateMeBtn" in r6.text
    assert "Select Tailor ✂️" in r6.text
    
    # Extract JSON tailor data to verify coordinates in Tamil Nadu
    data_start = r6.text.find('<script id="tailorsData" type="application/json">')
    data_content = r6.text[data_start:].split('</script>')[0].replace('<script id="tailorsData" type="application/json">', '').strip()
    tailors = json.loads(data_content)
    assert len(tailors) >= 30, f"Expected at least 30 tailors, found {len(tailors)}"
    for t in tailors[:5]:
        assert t["lat"] is not None and t["lng"] is not None
        assert 8.0 <= t["lat"] <= 14.0, f"Latitude {t['lat']} not within Tamil Nadu"
        assert 76.0 <= t["lng"] <= 81.0, f"Longitude {t['lng']} not within Tamil Nadu"
    print(f"PASS 6: Live Tamil Nadu map loaded with {len(tailors)} tailors verified across TN coordinates.")

    # 7. Request Custom Order Page (Styled, no raw HTML, 3D promise card)
    r7 = s.get(f"{BASE_URL}/orders/create")
    assert r7.status_code == 200
    assert "create-order-layout" in r7.text
    assert "order-clay-summary" in r7.text
    assert "tailor_id" in r7.text
    print("PASS 7: Custom tailoring order request page loaded with 3D styling and promise card.")

    # 8. Digital Measurement Vault Page
    r8 = s.get(f"{BASE_URL}/measurements")
    assert r8.status_code == 200
    assert "Digital Measurement Vault" in r8.text
    assert "Create New Profile" in r8.text
    print("PASS 8: Customer measurement section loaded with digital vault profiles.")

    # 9. Verify Footer links (Home, Dashboard, Logout) are removed from footer
    assert '<div class="footer-links">' not in r8.text, "Footer links should be removed from bottom"
    print("PASS 9: Verified footer does not display redundant duplicate navigation links.")

    # 10. Tailor Registration with Place & Area and Immediate Map Visibility
    import time
    ts = int(time.time())
    new_tailor_email = f"tailor_user_{ts}@test.com"
    s2 = requests.Session()
    r10_post = s2.post(f"{BASE_URL}/auth/register", data={
        "name": "Kovai Master Crafter",
        "email": new_tailor_email,
        "password": "password123",
        "confirm_password": "password123",
        "phone": "9843210987",
        "role": "tailor",
        "shop_name": f"Kovai Bespoke Atelier {ts}",
        "city": "Coimbatore",
        "area": "RS Puram",
        "address": "45 DB Road, RS Puram",
        "specialization": "Bespoke Men's Suits, Tuxedos, Formal Blazers",
        "terms": "1"
    }, allow_redirects=True)
    assert r10_post.status_code == 200

    # Fetch map and check if the newly registered tailor is immediately visible on map
    r10_map = s2.get(f"{BASE_URL}/customer/tailors")
    assert r10_map.status_code == 200
    assert f"Kovai Bespoke Atelier {ts}" in r10_map.text, "Newly registered tailor with place/area must be visible on the map"
    print("PASS 10: Tailor registration with place & area succeeds and immediately appears on Tamil Nadu map.")

    print("\nALL 10 END-TO-END SYSTEM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
