def get_persian_font(font=None):
    fallback_fonts = ["IrTitr", "Ordibehesht", "IRXLotus", "IRTabassom", "IRDastNevis", "IREntezar", "Behistun", "IRKamran", "IRMaryam", "Shekasteh_Beta", "IRAmir", "IranNastaliq-Web"]
    if font:
        return font
    for f in fallback_fonts:
        try:
            return f
        except Exception:
            continue
    raise ValueError("❌ هیچ فونت فارسی پیدا نشد. لطفن یک فونت فارسی نصب کنید! (e.g., Vazirmatn).")
