from app.models.party import Supplier

def test_purchase_order_and_goods_receipt(client, admin_headers, db_session):
    sup = db_session.query(Supplier).first()

    po_payload = {
        "supplier_id": sup.id,
        "tax_rate_pct": "3.00",
        "notes": "Procurement of Polished Rounds",
        "items": [
            {
                "item_type": "DIAMOND",
                "description": "1.00ct Round Diamonds Lot",
                "quantity": 5,
                "carat_weight": "5.0000",
                "unit_price": "150000.00",
                "line_total": "750000.00"
            }
        ]
    }
    po_res = client.post("/api/v1/purchases", json=po_payload, headers=admin_headers)
    assert po_res.status_code == 201
    po_data = po_res.json()
    assert po_data["status"] == "CONFIRMED"
    po_id = po_data["id"]

    # Confirm Goods Receipt
    gr_res = client.post("/api/v1/purchases/receive", json={"purchase_order_id": po_id, "notes": "Inspected & Verified"}, headers=admin_headers)
    assert gr_res.status_code == 201
    assert "GRN-" in gr_res.json()["receipt_number"]

    # Verify Stock Movement for Purchase Receipt
    mov_res = client.get("/api/v1/inventory/movements?movement_type=PURCHASE_RECEIPT", headers=admin_headers)
    assert mov_res.status_code == 200
    assert mov_res.json()["total"] >= 1

def test_dashboard_metrics(client, admin_headers):
    res = client.get("/api/v1/dashboard", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "inventory" in data
    assert "business" in data
    assert "category_distribution" in data
    assert "sales_trend" in data
    assert data["inventory"]["total_diamonds"] >= 1
    assert float(data["inventory"]["total_diamond_carats"]) > 0

def test_reports_csv_exports(client, admin_headers):
    dia_csv = client.get("/api/v1/reports/export/diamonds.csv", headers=admin_headers)
    assert dia_csv.status_code == 200
    assert "SKU,Shape,Carat Weight" in dia_csv.text

    sales_csv = client.get("/api/v1/reports/export/sales.csv", headers=admin_headers)
    assert sales_csv.status_code == 200
    assert "Order #,Date,Customer" in sales_csv.text
