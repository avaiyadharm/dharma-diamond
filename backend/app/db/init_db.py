from datetime import datetime, timezone
from decimal import Decimal
import logging
import os
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models import (
    User, Location, Supplier, Customer, Diamond, JewelleryProduct,
    JewelleryItem, JewelleryStone, Gemstone, StockMovement,
    SalesOrder, SalesOrderItem, Invoice, Payment
)
from app.core.security import get_password_hash
from app.core.permissions import UserRole

logger = logging.getLogger(__name__)


def _get_admin_email() -> str:
    return os.getenv("ADMIN_EMAIL") or settings.ADMIN_EMAIL


def _get_admin_password() -> str:
    return os.getenv("ADMIN_PASSWORD") or settings.ADMIN_PASSWORD


def init_db(db: Session) -> None:
    # 1. Create all tables
    Base.metadata.create_all(bind=engine)

    admin_email = _get_admin_email().strip().lower()
    admin_password = _get_admin_password()

    # 2. Seed a single administrator account using environment configuration.
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name=settings.ADMIN_FULL_NAME,
            role=UserRole.ADMIN.value,
            is_active=True,
            last_login_at=datetime.now(timezone.utc)
        )
        db.add(admin_user)
    else:
        admin_user.hashed_password = get_password_hash(admin_password)
        admin_user.full_name = settings.ADMIN_FULL_NAME
        admin_user.role = UserRole.ADMIN.value
        admin_user.is_active = True

    # A single-user app intentionally does not create a broad role hierarchy on startup.
    # Additional roles remain available for future extension, but the bootstrap is admin-only.
    db.flush()

    # 3. Seed locations
    loc_vault = db.query(Location).filter(Location.code == "MAIN_VAULT").first()
    if not loc_vault:
        loc_vault = Location(code="MAIN_VAULT", name="Main Vault - Master Safe", description="High security Class-1 vault", is_active=True)
        db.add(loc_vault)

    loc_display = db.query(Location).filter(Location.code == "DISPLAY_A").first()
    if not loc_display:
        loc_display = Location(code="DISPLAY_A", name="Showroom Counter A", description="Solitaires & Rings display", is_active=True)
        db.add(loc_display)

    loc_display_b = db.query(Location).filter(Location.code == "DISPLAY_B").first()
    if not loc_display_b:
        loc_display_b = Location(code="DISPLAY_B", name="Showroom Counter B", description="Necklaces & Bangles display", is_active=True)
        db.add(loc_display_b)

    db.flush()

    # 4. Seed suppliers
    sup_surat = db.query(Supplier).filter(Supplier.business_name == "Surat Diamond Exports Ltd").first()
    if not sup_surat:
        sup_surat = Supplier(
            business_name="Surat Diamond Exports Ltd",
            contact_person="Kishore Bhai",
            phone="+91 98250 11223",
            email="kishore@suratdiamondexports.com",
            address="G-12 Diamond Bourse, Khajod, Surat, Gujarat 395007",
            tax_id="24AAACS1234F1Z5",
            country="India",
            currency="INR",
            category="Rough & Polished Diamonds",
            payment_terms="Net 30 Days"
        )
        db.add(sup_surat)

    sup_mumbai = db.query(Supplier).filter(Supplier.business_name == "Mumbai Bullion & Casting Works").first()
    if not sup_mumbai:
        sup_mumbai = Supplier(
            business_name="Mumbai Bullion & Casting Works",
            contact_person="Vikram Mehta",
            phone="+91 98190 44556",
            email="orders@mumbaibullion.in",
            address="45 Zaveri Bazaar, Kalbadevi, Mumbai 400002",
            tax_id="27AABCM5678G1Z2",
            country="India",
            currency="INR",
            category="Gold Mountings & Casting",
            payment_terms="Net 15 Days"
        )
        db.add(sup_mumbai)

    # 5. Seed customers
    cust_amitabh = db.query(Customer).filter(Customer.name == "Amitabh Singhania").first()
    if not cust_amitabh:
        cust_amitabh = Customer(
            name="Amitabh Singhania",
            company_name="Singhania Jewels",
            phone="+91 98200 99887",
            email="amitabh@singhaniajewels.com",
            billing_address="Flat 14A, Sea Face Towers, Worli, Mumbai 400018",
            customer_type="Wholesale",
            tax_id="27AAAPS9876Q1Z9"
        )
        db.add(cust_amitabh)

    cust_priya = db.query(Customer).filter(Customer.name == "Priya Kapoor").first()
    if not cust_priya:
        cust_priya = Customer(
            name="Priya Kapoor",
            phone="+91 99100 23456",
            email="priya.kapoor@gmail.com",
            billing_address="B-42 Greater Kailash I, New Delhi 110048",
            customer_type="Retail"
        )
        db.add(cust_priya)

    db.flush()

    # 6. Seed certified diamonds if empty
    if db.query(Diamond).count() == 0:
        sample_diamonds = [
            {
                "sku": "DIA-2026-001",
                "shape": "Round",
                "carat_weight": Decimal("1.5000"),
                "available_carats": Decimal("1.5000"),
                "color_grade": "D",
                "clarity_grade": "VVS1",
                "cut_grade": "Excellent",
                "polish": "Excellent",
                "symmetry": "Excellent",
                "fluorescence": "None",
                "measurements_mm": "7.32 x 7.36 x 4.54 mm",
                "table_pct": Decimal("57.0"),
                "depth_pct": Decimal("61.8"),
                "diamond_type": "Natural",
                "certificate_lab": "GIA",
                "certificate_number": "GIA-2195048101",
                "purchase_cost": Decimal("480000.00"),
                "calculated_acquisition_cost": Decimal("485000.00"),
                "asking_price": Decimal("680000.00"),
                "min_selling_price": Decimal("640000.00"),
                "status": "AVAILABLE",
                "location_id": loc_vault.id,
                "supplier_id": sup_surat.id,
                "notes": "Triple Excellent cut. Superb brilliance, completely eye-clean."
            },
            {
                "sku": "DIA-2026-002",
                "shape": "Oval",
                "carat_weight": Decimal("2.0200"),
                "available_carats": Decimal("2.0200"),
                "color_grade": "E",
                "clarity_grade": "VS1",
                "cut_grade": "Excellent",
                "polish": "Excellent",
                "symmetry": "Very Good",
                "fluorescence": "Faint",
                "measurements_mm": "10.15 x 7.12 x 4.45 mm",
                "table_pct": Decimal("59.0"),
                "depth_pct": Decimal("62.5"),
                "diamond_type": "Natural",
                "certificate_lab": "IGI",
                "certificate_number": "IGI-562984112",
                "purchase_cost": Decimal("720000.00"),
                "calculated_acquisition_cost": Decimal("728000.00"),
                "asking_price": Decimal("990000.00"),
                "min_selling_price": Decimal("940000.00"),
                "status": "AVAILABLE",
                "location_id": loc_display.id,
                "supplier_id": sup_surat.id,
                "notes": "Ideal 1.42 length-to-width ratio. Minimal bowtie effect."
            },
            {
                "sku": "DIA-2026-003",
                "shape": "Emerald",
                "carat_weight": Decimal("3.0500"),
                "available_carats": Decimal("3.0500"),
                "color_grade": "F",
                "clarity_grade": "VVS2",
                "cut_grade": "Excellent",
                "polish": "Excellent",
                "symmetry": "Excellent",
                "fluorescence": "None",
                "measurements_mm": "9.85 x 7.02 x 4.75 mm",
                "table_pct": Decimal("64.0"),
                "depth_pct": Decimal("67.6"),
                "diamond_type": "Natural",
                "certificate_lab": "GIA",
                "certificate_number": "GIA-1184905224",
                "purchase_cost": Decimal("1650000.00"),
                "calculated_acquisition_cost": Decimal("1665000.00"),
                "asking_price": Decimal("2250000.00"),
                "min_selling_price": Decimal("2100000.00"),
                "status": "AVAILABLE",
                "location_id": loc_vault.id,
                "supplier_id": sup_surat.id,
                "notes": "Classic step cut with mirror-like hall-of-mirrors facet reflection."
            },
            {
                "sku": "DIA-2026-004",
                "shape": "Princess",
                "carat_weight": Decimal("1.0200"),
                "available_carats": Decimal("1.0200"),
                "color_grade": "G",
                "clarity_grade": "VS2",
                "cut_grade": "Very Good",
                "polish": "Excellent",
                "symmetry": "Excellent",
                "fluorescence": "None",
                "measurements_mm": "5.62 x 5.58 x 4.02 mm",
                "table_pct": Decimal("71.0"),
                "depth_pct": Decimal("72.0"),
                "diamond_type": "Natural",
                "certificate_lab": "HRD",
                "certificate_number": "HRD-882039102",
                "purchase_cost": Decimal("210000.00"),
                "calculated_acquisition_cost": Decimal("212000.00"),
                "asking_price": Decimal("310000.00"),
                "min_selling_price": Decimal("290000.00"),
                "status": "AVAILABLE",
                "location_id": loc_vault.id,
                "supplier_id": sup_surat.id,
                "notes": "Square modified brilliant cut with sharp, clean corners."
            },
            {
                "sku": "DIA-2026-005",
                "shape": "Round",
                "carat_weight": Decimal("2.5000"),
                "available_carats": Decimal("2.5000"),
                "color_grade": "E",
                "clarity_grade": "VVS2",
                "cut_grade": "Ideal",
                "polish": "Excellent",
                "symmetry": "Excellent",
                "fluorescence": "None",
                "measurements_mm": "8.75 x 8.78 x 5.39 mm",
                "table_pct": Decimal("56.0"),
                "depth_pct": Decimal("61.5"),
                "diamond_type": "Lab_Grown",
                "certificate_lab": "IGI",
                "certificate_number": "LG-598201452",
                "purchase_cost": Decimal("180000.00"),
                "calculated_acquisition_cost": Decimal("182000.00"),
                "asking_price": Decimal("275000.00"),
                "min_selling_price": Decimal("255000.00"),
                "status": "AVAILABLE",
                "location_id": loc_display.id,
                "supplier_id": sup_surat.id,
                "notes": "Type IIa CVD Lab-Grown solitaire diamond. Zero nitrogen impurities."
            }
        ]
        for d_data in sample_diamonds:
            dia = Diamond(**d_data)
            db.add(dia)
            db.flush()
            # Movement
            mov = StockMovement(
                movement_number=f"MOV-INIT-{dia.sku}",
                item_type="DIAMOND",
                diamond_id=dia.id,
                movement_type="OPENING_STOCK",
                qty_before=0,
                qty_change=1,
                qty_after=1,
                carat_change=dia.carat_weight,
                destination_location_id=dia.location_id,
                user_id=admin_user.id,
                reason="Initial Vault Stock Inward"
            )
            db.add(mov)

    # 7. Seed Jewellery Catalog & Physical Serialized Items if empty
    if db.query(JewelleryProduct).count() == 0:
        prod_ring = JewelleryProduct(
            design_code="DES-RNG-01",
            name="The Royal Cathedral Solitaire Ring",
            category="Ring",
            collection="Dharma Heritage 2026",
            metal_type="Gold",
            purity="18K",
            description="Four-prong cathedral mount setting with subtle pavé diamonds along the shank.",
            image_url="https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80"
        )
        prod_necklace = JewelleryProduct(
            design_code="DES-NCK-02",
            name="Imperial Riviera Diamond Necklace",
            category="Necklace",
            collection="Signature Haute Joaillerie",
            metal_type="Gold",
            purity="18K",
            description="Graduated round brilliant diamonds set in articulated three-prong white gold bezels.",
            image_url="https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80"
        )
        prod_earrings = JewelleryProduct(
            design_code="DES-EAR-03",
            name="Celestial Halo Solitaire Studs",
            category="Earrings",
            collection="Daily Solitaires",
            metal_type="Platinum",
            purity="950 Pt",
            description="Classic screw-back studs with micro-pavé halo frame around central stones.",
            image_url="https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"
        )
        db.add_all([prod_ring, prod_necklace, prod_earrings])
        db.flush()

        # Physical piece 1: Ring
        item_ring = JewelleryItem(
            sku="JWL-2026-001",
            product_id=prod_ring.id,
            gross_weight_grams=Decimal("4.8500"),
            net_metal_weight_grams=Decimal("4.5500"),
            total_stone_carats=Decimal("1.5000"),
            hallmark_details="BIS 750 (18K White Gold)",
            metal_cost=Decimal("31850.00"),
            stone_cost=Decimal("485000.00"),
            making_charge=Decimal("18500.00"),
            other_costs=Decimal("2500.00"),
            total_cost=Decimal("537850.00"),
            selling_price=Decimal("780000.00"),
            status="AVAILABLE",
            location_id=loc_display.id,
            supplier_id=sup_mumbai.id,
            notes="Ready for delivery. Finger size 14 Indian standard."
        )
        db.add(item_ring)
        db.flush()

        stone1 = JewelleryStone(
            jewellery_item_id=item_ring.id,
            stone_type="Diamond",
            stone_count=1,
            carat_weight=Decimal("1.2000"),
            shape="Round",
            color="D",
            clarity="VVS1",
            setting_type="Prong"
        )
        stone2 = JewelleryStone(
            jewellery_item_id=item_ring.id,
            stone_type="Diamond",
            stone_count=16,
            carat_weight=Decimal("0.3000"),
            shape="Round",
            color="F",
            clarity="VS1",
            setting_type="Pave"
        )
        db.add_all([stone1, stone2])

        # Physical piece 2: Riviera Necklace
        item_necklace = JewelleryItem(
            sku="JWL-2026-002",
            product_id=prod_necklace.id,
            gross_weight_grams=Decimal("28.4500"),
            net_metal_weight_grams=Decimal("25.2500"),
            total_stone_carats=Decimal("16.0000"),
            hallmark_details="BIS 750 (18K Rose Gold)",
            metal_cost=Decimal("176750.00"),
            stone_cost=Decimal("1250000.00"),
            making_charge=Decimal("65000.00"),
            other_costs=Decimal("8250.00"),
            total_cost=Decimal("1500000.00"),
            selling_price=Decimal("2150000.00"),
            status="AVAILABLE",
            location_id=loc_display_b.id,
            supplier_id=sup_mumbai.id,
            notes="110 graduated round brilliant diamonds total 16.00 carats."
        )
        db.add(item_necklace)
        db.flush()

        stone_neck = JewelleryStone(
            jewellery_item_id=item_necklace.id,
            stone_type="Diamond",
            stone_count=110,
            carat_weight=Decimal("16.0000"),
            shape="Round",
            color="G",
            clarity="VS2",
            setting_type="Prong"
        )
        db.add(stone_neck)

    # 8. Seed loose gemstones if empty
    if db.query(Gemstone).count() == 0:
        sample_gems = [
            {
                "sku": "GEM-2026-001",
                "gemstone_type": "Ruby",
                "variety": "Burmese Pigeon Blood Ruby",
                "is_natural": True,
                "carat_weight": Decimal("2.1400"),
                "shape": "Cushion",
                "color": "Vivid Red",
                "clarity": "Eye Clean",
                "cut": "Mixed Brilliant",
                "treatment": "Unheated",
                "certificate_lab": "GIA",
                "certificate_number": "GIA-GEM-88129",
                "purchase_cost": Decimal("380000.00"),
                "selling_price": Decimal("550000.00"),
                "status": "AVAILABLE",
                "location_id": loc_vault.id,
                "supplier_id": sup_surat.id,
                "notes": "Exceptional fluorescent glow under natural daylight."
            },
            {
                "sku": "GEM-2026-002",
                "gemstone_type": "Emerald",
                "variety": "Zambian Emerald",
                "is_natural": True,
                "carat_weight": Decimal("3.4200"),
                "shape": "Emerald Cut",
                "color": "Deep Vivid Green",
                "clarity": "Minor Jardin",
                "cut": "Step Cut",
                "treatment": "Minor Cedarwood Oil",
                "certificate_lab": "IGI",
                "certificate_number": "IGI-EM-40291",
                "purchase_cost": Decimal("290000.00"),
                "selling_price": Decimal("420000.00"),
                "status": "AVAILABLE",
                "location_id": loc_vault.id,
                "supplier_id": sup_surat.id,
                "notes": "Lush saturated green tone with high transparency."
            }
        ]
        for g_data in sample_gems:
            gem = Gemstone(**g_data)
            db.add(gem)

    db.commit()
    logger.info("Database initialized with real business seed data.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
