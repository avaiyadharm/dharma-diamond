from decimal import Decimal
from app.models.diamond import Diamond
from app.models.party import Customer

def test_cancel_sale_rejects_invalid_inventory_state(client, admin_headers, sales_headers, db_session):
    dia_payload = {
        "sku": "DIA-SALE-CANCEL-001",
        "shape": "Round",
        "carat_weight": "1.0500",
        "color_grade": "G",
        "clarity_grade": "VS1",
        "purchase_cost": "250000.00",
        "calculated_acquisition_cost": "260000.00",
        "asking_price": "420000.00"
    }
    dia_res = client.post("/api/v1/diamonds", json=dia_payload, headers=admin_headers)
    assert dia_res.status_code == 201
    dia_id = dia_res.json()["id"]

    cust = db_session.query(Customer).first()
    sale_payload = {
        "customer_id": cust.id,
        "tax_rate_pct": "3.00",
        "initial_payment_amount": "0.00",
        "items": [
            {
                "item_type": "DIAMOND",
                "diamond_id": dia_id,
                "sku": "DIA-SALE-CANCEL-001",
                "description": "1.05ct Round G/VS1",
                "quantity": 1,
                "unit_price": "420000.00",
                "discount": "0.00"
            }
        ]
    }

    sale_res = client.post("/api/v1/sales", json=sale_payload, headers=sales_headers)
    assert sale_res.status_code == 201
    so_id = sale_res.json()["id"]

    diamond = db_session.query(Diamond).filter(Diamond.id == dia_id).first()
    diamond.status = "RETURNED_PENDING_INSPECTION"
    db_session.commit()

    cancel_res = client.post(f"/api/v1/sales/{so_id}/cancel", json={"reason": "Customer requested cancellation after return review"}, headers=admin_headers)
    assert cancel_res.status_code == 400
    assert "cannot cancel sale" in cancel_res.json()["detail"].lower()


def test_atomic_sale_workflow_and_cogs(client, admin_headers, sales_headers, db_session):
    # 1. Add a diamond to sell
    dia_payload = {
        "sku": "DIA-SALE-001",
        "shape": "Round",
        "carat_weight": "2.0100",
        "color_grade": "F",
        "clarity_grade": "VVS2",
        "purchase_cost": "700000.00",
        "calculated_acquisition_cost": "710000.00",
        "asking_price": "950000.00"
    }
    dia_res = client.post("/api/v1/diamonds", json=dia_payload, headers=admin_headers)
    assert dia_res.status_code == 201
    dia_id = dia_res.json()["id"]

    cust = db_session.query(Customer).first()

    # 2. Finalize Sale
    sale_payload = {
        "customer_id": cust.id,
        "tax_rate_pct": "3.00",
        "discount_amount": "20000.00",
        "initial_payment_amount": "500000.00",
        "payment_method": "Bank Transfer",
        "notes": "VIP Solitaire Purchase",
        "items": [
            {
                "item_type": "DIAMOND",
                "diamond_id": dia_id,
                "sku": "DIA-SALE-001",
                "description": "2.01ct Round F/VVS2 Solitaire",
                "quantity": 1,
                "unit_price": "950000.00",
                "discount": "0.00"
            }
        ]
    }
    sale_res = client.post("/api/v1/sales", json=sale_payload, headers=sales_headers)
    assert sale_res.status_code == 201
    sale_data = sale_res.json()
    assert sale_data["status"] == "CONFIRMED"
    assert sale_data["payment_status"] == "PARTIALLY_PAID"

    # Verify COGS snapshot was locked
    cogs_captured = Decimal(str(sale_data["items"][0]["cost_price"]))
    assert cogs_captured == Decimal("710000.00")

    # Verify Diamond status is now SOLD
    dia_check = client.get(f"/api/v1/diamonds/{dia_id}", headers=sales_headers)
    assert dia_check.json()["status"] == "SOLD"

    # 3. DOUBLE-SELLING PREVENTION TEST: Attempt to sell the same diamond again!
    dup_sale = client.post("/api/v1/sales", json=sale_payload, headers=sales_headers)
    assert dup_sale.status_code == 400
    assert "cannot be sold" in dup_sale.json()["detail"]

    # 4. Verify Stock Movement was recorded
    mov_res = client.get("/api/v1/inventory/movements?item_type=DIAMOND", headers=sales_headers)
    assert mov_res.status_code == 200
    sale_movements = [m for m in mov_res.json()["items"] if m["movement_type"] == "SALE" and m["item_sku"] == "DIA-SALE-001"]
    assert len(sale_movements) == 1
    assert sale_movements[0]["qty_change"] == -1

    # 5. Verify Invoice and Balance Due
    inv_res = client.get(f"/api/v1/invoices?customer_id={cust.id}", headers=sales_headers)
    assert inv_res.status_code == 200
    assert inv_res.json()["total"] >= 1
    latest_inv = inv_res.json()["items"][0]
    assert float(latest_inv["amount_paid"]) == 500000.00
    assert float(latest_inv["balance_due"]) > 0

    # 6. Settle remaining balance
    pay_res = client.post(
        "/api/v1/payments",
        json={
            "payment_type": "CUSTOMER_PAYMENT",
            "invoice_id": latest_inv["id"],
            "amount": str(latest_inv["balance_due"]),
            "payment_method": "UPI",
            "reference_number": "UPI/2026/889900"
        },
        headers=sales_headers
    )
    assert pay_res.status_code == 201

    # Verify invoice is now PAID
    inv_check = client.get(f"/api/v1/invoices?customer_id={cust.id}", headers=sales_headers)
    settled_inv = [i for i in inv_check.json()["items"] if i["id"] == latest_inv["id"]][0]
    assert settled_inv["status"] == "PAID"
    assert float(settled_inv["balance_due"]) == 0.00
