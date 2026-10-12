def test_create_and_fetch_diamond(client, admin_headers):
    payload = {
        "sku": "DIA-TEST-1001",
        "shape": "Round",
        "carat_weight": "1.5200",
        "color_grade": "D",
        "clarity_grade": "VVS1",
        "cut_grade": "Excellent",
        "polish": "Excellent",
        "symmetry": "Excellent",
        "fluorescence": "None",
        "certificate_lab": "GIA",
        "certificate_number": "GIA-2195048123",
        "purchase_cost": "450000.00",
        "asking_price": "620000.00"
    }
    create_res = client.post("/api/v1/diamonds", json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["sku"] == "DIA-TEST-1001"
    assert created["status"] == "AVAILABLE"
    assert float(created["available_carats"]) == 1.52

    # Verify duplicate SKU rejected
    dup_res = client.post("/api/v1/diamonds", json=payload, headers=admin_headers)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # Verify duplicate certificate number rejected
    payload_dup_cert = dict(payload)
    payload_dup_cert["sku"] = "DIA-TEST-DIFF-SKU"
    dup_cert_res = client.post("/api/v1/diamonds", json=payload_dup_cert, headers=admin_headers)
    assert dup_cert_res.status_code == 400
    assert "Certificate" in dup_cert_res.json()["detail"]

def test_search_diamonds_by_cert_and_carat(client, admin_headers):
    # Search by certificate number
    res = client.get("/api/v1/diamonds?query=2195048123", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["sku"] == "DIA-TEST-1001"

    # Search by carat range
    res_range = client.get("/api/v1/diamonds?min_carat=1.00&max_carat=2.00", headers=admin_headers)
    assert res_range.status_code == 200
    assert res_range.json()["total"] >= 1

def test_reserve_and_release_diamond(client, admin_headers, sales_headers, db_session):
    from app.models.party import Customer
    from app.models.diamond import Diamond

    cust = db_session.query(Customer).first()
    dia = db_session.query(Diamond).filter(Diamond.sku == "DIA-TEST-1001").first()

    # Reserve diamond
    res_reserve = client.post(
        f"/api/v1/diamonds/{dia.id}/reserve",
        json={"customer_id": cust.id, "expires_in_hours": 24},
        headers=sales_headers
    )
    assert res_reserve.status_code == 200
    assert res_reserve.json()["status"] == "ACTIVE"

    # Verify diamond status is now RESERVED
    check_res = client.get(f"/api/v1/diamonds/{dia.id}", headers=sales_headers)
    assert check_res.json()["status"] == "RESERVED"

    # Release reservation
    res_release = client.post(f"/api/v1/diamonds/{dia.id}/release", headers=sales_headers)
    assert res_release.status_code == 200

    check_res2 = client.get(f"/api/v1/diamonds/{dia.id}", headers=sales_headers)
    assert check_res2.json()["status"] == "AVAILABLE"

def test_readonly_user_cannot_create_diamond(client, readonly_headers):
    payload = {
        "sku": "DIA-RO-FAIL",
        "shape": "Oval",
        "carat_weight": "1.0000",
        "color_grade": "E",
        "clarity_grade": "VS1",
        "purchase_cost": "200000.00",
        "asking_price": "280000.00"
    }
    res = client.post("/api/v1/diamonds", json=payload, headers=readonly_headers)
    assert res.status_code == 403
