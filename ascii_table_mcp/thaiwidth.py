#!/usr/bin/env python3
"""Thai-aware display width: zero-width marks → width 1.

wcwidth() ระบุว่าสระบน/ล่าง วรรณยุกต์ และเครื่องหมายซ้อนของไทยมี width=0
ถูกต้องตาม Unicode spec แต่ในทางปฏิบัติ (terminal, Discord, browser)
คนไทยเห็น 1 ช่องพอดี — เวลาจัดตารางจึงต้อง +1 ให้ตรงกับที่ตาเห็น

ฟังก์ชันนี้ใช้ wcwidth สำหรับ non-Thai (CJK = 2, ASCII = 1, etc.)
และ override เฉพาะ zero-width Thai 16 ตัวให้ width=1

Usage:
    from thaiwidth import thai_width
    w = thai_width("ก๋วยเตี๋ยว")  # → 10 (len ก็ 10)
    w = thai_width("你好")        # → 4 (CJK ยัง width=2)
    w = thai_width("abc")        # → 3
"""

import sys

try:
    from wcwidth import wcwidth as _wcwidth_core, wcswidth as _wcswidth_core
except ImportError:
    _wcwidth_core = None
    _wcswidth_core = None


# ─── Thai zero-width override ──────────────────────────────────────────
# 16 ตัวอักษรไทยที่ wcwidth=0 แต่สายตามนุษย์เห็น width=1
# ช่วง U+0E31 + U+0E34–0E3A (สระบน/ล่าง) และ U+0E47–0E4E (วรรณยุกต์ + เครื่องหมาย)
#
# แยกตามประเภท:
#   สระบน:     ◌ั ◌ิ ◌ี ◌ึ ◌ื        (U+0E31, 0E34–0E37)
#   สระล่าง:   ◌ุ ◌ู ◌ฺ              (U+0E38–0E3A)
#   วรรณยุกต์: ◌่ ◌้ ◌๊ ◌๋            (U+0E48–0E4B)
#   ไม้ไต่คู้: ◌็                   (U+0E47)
#   การันต์:   ◌์                   (U+0E4C)
#   นิคหิต:    ◌ํ                   (U+0E4D)
#   ยามักการ:  ◌๎                   (U+0E4E)
THAI_ZERO_TO_ONE = frozenset(
    range(0x0E31, 0x0E3B)  # ั ิ ี ึ ื ุ ู ฺ (8 ตัว)
) | frozenset(
    range(0x0E47, 0x0E4F)  # ็ ่ ้ ๊ ๋ ์ ํ ๎ (8 ตัว)
)

# รวมเป็น tuple สำหรับ performance (ไม่ต้อง union ทุกครั้ง)
_THAI_OVERRIDE_CODEPOINTS = tuple(sorted(THAI_ZERO_TO_ONE))


def is_thai_zero_width(ch: str) -> bool:
    """True ถ้า ch เป็น zero-width Thai ที่ควรนับ width=1"""
    return ord(ch) in THAI_ZERO_TO_ONE


def thai_width(s: str, mode: str = 'auto', thai_coeff: float = 1.0) -> int:
    """Display width สำหรับข้อความ — รองรับ Discord font fallback.

    Args:
        s: ข้อความ (string)
        mode: 'auto' (default) — zero-width marks = 1, CJK = 2
              'discord' — ใช้ per-character ratio จาก Leelawadee font
        thai_coeff: ตัวคูณความกว้างสำหรับทุกตัวอักษรไทย (U+0E00–U+0E7F)
                    1.0 = wcwidth (default, zero-width = 1)
                    1.5 = fixed 1.5× สำหรับทุกตัว → จัดตาราง stable บน Discord
                    ค่า > 1.0 ใช้ ceil() ปัดเศษขึ้น

    Returns:
        ความกว้างในหน่วย character cells (terminal/table)
    """
    import math

    if not s:
        return 0

    # thai_coeff > 1.0: fixed coefficient สำหรับทุกตัวอักษรไทย
    # แก้ proportional font problem (ญ=1.5×, เ=0.48×)
    # ทุกตัวไทยนับเท่ากันหมด → table stable
    if thai_coeff > 1.0:
        total = 0.0
        for ch in str(s):
            cp = ord(ch)
            if 0x0E00 <= cp <= 0x0E7F:
                total += thai_coeff
            elif _wcwidth_core is not None:
                w = _wcwidth_core(ch)
                total += w if w >= 0 else 1.0
            else:
                total += 1.0
        return math.ceil(total)

    if mode == 'discord':
        # ใช้ len() + extra สำหรับ chars ที่มี ratio > 1.3 (overflow ชัดเจน)
        total = 0.0
        for ch in str(s):
            cp = ord(ch)
            ratio = THAI_DISCORD_RATIO.get(cp)
            if ratio is not None:
                if ratio > 1.3:
                    total += 2.0  # chars ที่ล้นมาก: ญ ณ ฌ ฒ ๗ ๛
                else:
                    total += 1.0  # รวม combining marks
            elif _wcwidth_core is not None:
                w = _wcwidth_core(ch)
                total += w if w >= 0 else 1.0
            else:
                total += 1.0
        return int(total)

    # Default 'auto' mode: zero-width marks → 1, CJK → 2
    total = 0
    for ch in str(s):
        cp = ord(ch)
        if cp in THAI_ZERO_TO_ONE:
            total += 1
        elif _wcwidth_core is not None:
            w = _wcwidth_core(ch)
            total += w if w >= 0 else 1
        else:
            total += 1
    return total


def thai_wcswidth(s: str) -> int:
    """Alias สำหรับ thai_width — เพื่อความเข้ากับ wcswidth API"""
    return thai_width(s)


# ─── Unicode block ตรวจสอบ ─────────────────────────────────────────────

THAI_CHAR_NAMES: dict[int, str] = {
    0x0E31: "ไม้หันอากาศ (mai han akat)",
    0x0E34: "สระอิ (sara i)",
    0x0E35: "สระอี (sara ii)",
    0x0E36: "สระอึ (sara ue)",
    0x0E37: "สระอื (sara uee)",
    0x0E38: "สระอุ (sara u)",
    0x0E39: "สระอู (sara uu)",
    0x0E3A: "พินทุ (phinthu)",
    0x0E47: "ไม้ไต่คู้ (mai taikhu)",
    0x0E48: "ไม้เอก (mai ek)",
    0x0E49: "ไม้โท (mai tho)",
    0x0E4A: "ไม้ตรี (mai tri)",
    0x0E4B: "ไม้จัตวา (mai chattawa)",
    0x0E4C: "ทัณฑฆาต/การันต์ (thanthakhat)",
    0x0E4D: "นิคหิต/นฤคหิต (nikhahit)",
    0x0E4E: "ยามักการ (yamakkan)",
}


def describe(s: str) -> str:
    """ตรวจสอบข้อความ — คืนค่ารายงานว่ามี Thai zero-width char กี่ตัว

    ใช้ตอน debug ว่าข้อความมีสระ/วรรณยุกต์เยอะแค่ไหน
    """
    count = 0
    found = []
    for ch in set(s):
        cp = ord(ch)
        if cp in THAI_CHAR_NAMES:
            count += s.count(ch)
            found.append((repr(ch), THAI_CHAR_NAMES[cp], s.count(ch)))
    w = thai_width(s)
    raw = _wcswidth_core(s) if _wcswidth_core is not None else len(s)
    return (
        f"thai_width={w}, wcwidth(ดิบ)={raw}, len={len(s)}, "
        f"zero-width chars: {count} ตัว"
    )


# ─── Discord font fallback compensation ──────────────────────────────
# Windows ไม่มี monospace font ที่รองรับภาษาไทย
# เวลา Discord render code block:
#   ASCII → Consolas (monospace, ทุกตัวกว้าง 1126 font units)
#   ไทย   → Leelawadee (proportional, แต่ละตัวกว้างไม่เท่ากัน)
#
# ratio = advance_in_Leelawadee / 1126 (Consolas cell width)
# ratio > 1.0 → ตัวอักษรล้น cell → text ดูเลื่อนไปขวา
# ratio < 1.0 → ตัวอักษรแคบ → มีช่องว่าง
#
# ตัวที่แย่ที่สุด: ณ (1.622×), ๛ (1.619×), ฒ (1.544×), ฌ (1.512×), ญ (1.500×)
# ตัวที่แคบ: ะ (0.622×), เ (0.483×), ง (0.706×)
#
# ที่มา: fontTools วัดจาก Consolas vs Leelawadee บน Windows 10
THAI_DISCORD_RATIO: dict[int, float] = {
    0x0E01: 1.044,  # ก
    0x0E02: 1.097,  # ข
    0x0E03: 1.119,  # ฃ
    0x0E04: 1.045,  # ค
    0x0E05: 1.045,  # ฅ
    0x0E06: 1.126,  # ฆ
    0x0E07: 0.706,  # ง
    0x0E08: 0.925,  # จ
    0x0E09: 1.125,  # ฉ
    0x0E0A: 1.093,  # ช
    0x0E0B: 1.107,  # ซ
    0x0E0C: 1.512,  # ฌ
    0x0E0D: 1.500,  # ญ
    0x0E0E: 1.088,  # ฎ
    0x0E0F: 1.088,  # ฏ
    0x0E10: 0.885,  # ฐ
    0x0E11: 1.234,  # ฑ
    0x0E12: 1.544,  # ฒ
    0x0E13: 1.622,  # ณ
    0x0E14: 1.045,  # ด
    0x0E15: 1.045,  # ต
    0x0E16: 1.044,  # ถ
    0x0E17: 1.073,  # ท
    0x0E18: 0.927,  # ธ
    0x0E19: 1.080,  # น
    0x0E1A: 1.035,  # บ
    0x0E1B: 1.035,  # ป
    0x0E1C: 1.088,  # ผ
    0x0E1D: 1.088,  # ฝ
    0x0E1E: 1.214,  # พ
    0x0E1F: 1.214,  # ฟ
    0x0E20: 1.088,  # ภ
    0x0E21: 1.020,  # ม
    0x0E22: 0.953,  # ย
    0x0E23: 0.781,  # ร
    0x0E24: 1.044,  # ฤ
    0x0E25: 0.980,  # ล
    0x0E26: 1.088,  # ฦ
    0x0E27: 0.828,  # ว
    0x0E28: 1.048,  # ศ
    0x0E29: 1.074,  # ษ
    0x0E2A: 0.980,  # ส
    0x0E2B: 1.072,  # ห
    0x0E2C: 1.218,  # ฬ
    0x0E2D: 0.961,  # อ
    0x0E2E: 0.978,  # ฮ
    0x0E2F: 0.919,  # ฯ
    0x0E30: 0.622,  # ะ
    0x0E31: 0.000,  # ◌ั (combining)
    0x0E32: 0.828,  # ◌า
    0x0E33: 0.828,  # ◌ำ
    0x0E34: 0.000,  # ◌ิ (combining)
    0x0E35: 0.000,  # ◌ี (combining)
    0x0E36: 0.000,  # ◌ึ (combining)
    0x0E37: 0.000,  # ◌ื (combining)
    0x0E38: 0.000,  # ◌ุ (combining)
    0x0E39: 0.000,  # ◌ู (combining)
    0x0E3A: 0.000,  # ◌ฺ (combining)
    0x0E3F: 1.060,  # ฿
    0x0E40: 0.483,  # ◌เ
    0x0E41: 0.878,  # ◌แ
    0x0E42: 0.744,  # ◌โ
    0x0E43: 0.711,  # ◌ใ
    0x0E44: 0.726,  # ◌ไ
    0x0E45: 0.828,  # ◌ๅ
    0x0E46: 0.807,  # ◌ๆ
    0x0E47: 0.000,  # ◌็ (combining)
    0x0E48: 0.000,  # ◌่ (combining)
    0x0E49: 0.000,  # ◌้ (combining)
    0x0E4A: 0.000,  # ◌๊ (combining)
    0x0E4B: 0.000,  # ◌๋ (combining)
    0x0E4C: 0.000,  # ◌์ (combining)
    0x0E4D: 0.000,  # ◌ํ (combining)
    0x0E4E: 0.000,  # ◌๎ (combining)
    0x0E4F: 0.984,  # ◌๏
    0x0E50: 1.020,  # ◌๐
    0x0E51: 1.115,  # ◌๑
    0x0E52: 1.174,  # ◌๒
    0x0E53: 1.081,  # ◌๓
    0x0E54: 1.084,  # ◌๔
    0x0E55: 1.084,  # ◌๕
    0x0E56: 0.890,  # ◌๖
    0x0E57: 1.326,  # ◌๗
    0x0E58: 1.143,  # ◌๘
    0x0E59: 1.126,  # ◌๙
    0x0E5A: 1.176,  # ◌๚
    0x0E5B: 1.619,  # ◌๛
}


def discord_width(s: str) -> float:
    """Effective display width ใน Discord code block (fractional cells).

    ชดเชย font fallback: ไทย→Leelawadee (proportional), ASCII→Consolas (monospace)
    คืนค่าเป็น float (เช่น 6.134 = ~6⅛ cells) ต้อง ceil() ก่อนใช้จริง
    """
    total = 0.0
    for ch in str(s):
        cp = ord(ch)
        ratio = THAI_DISCORD_RATIO.get(cp)
        if ratio is not None:
            total += ratio
        elif _wcwidth_core is not None:
            w = _wcwidth_core(ch)
            total += w if w >= 0 else 1.0
        else:
            total += 1.0
    return total


# ─── CLI: ใช้ `python3 thaiwidth.py "ข้อความ"` ────────────────────────

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        w = thai_width(arg)
        print(f"{repr(arg):30s} → thai_width={w}, len={len(arg)}")
