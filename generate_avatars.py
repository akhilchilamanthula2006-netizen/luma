import os

AVATAR_DIR = r"c:\Users\AKHIL\OneDrive\Desktop\luma\static\images\avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)

def create_svg(bg_color_1, bg_color_2, shirt_color, skin_color, neck_color, hair_color, hair_d, eyebrows_d, eyes_svg, nose_d, mouth_d, extra_svg=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
  <defs>
    <clipPath id="clip"><circle cx="60" cy="60" r="58"/></clipPath>
    <radialGradient id="grad" cx="50%" cy="30%" r="70%">
      <stop offset="0%" stop-color="{bg_color_1}"/>
      <stop offset="100%" stop-color="{bg_color_2}"/>
    </radialGradient>
  </defs>
  <circle cx="60" cy="60" r="58" fill="url(#grad)"/>
  <g clip-path="url(#clip)">
    <!-- Shirt -->
    <path d="M18 122 Q18 90 60 88 Q102 90 102 122Z" fill="{shirt_color}"/>
    <!-- Neck -->
    <rect x="52" y="72" width="16" height="18" rx="4" fill="{neck_color}"/>
    <!-- Head -->
    <ellipse cx="60" cy="54" rx="24" ry="27" fill="{skin_color}"/>
    <!-- Ears -->
    <ellipse cx="36" cy="55" rx="5" ry="6" fill="{neck_color}"/>
    <ellipse cx="36" cy="55" rx="3" ry="4" fill="{skin_color}"/>
    <ellipse cx="84" cy="55" rx="5" ry="6" fill="{neck_color}"/>
    <ellipse cx="84" cy="55" rx="3" ry="4" fill="{skin_color}"/>
    <!-- Hair Base / Hair Back -->
    {hair_d}
    <!-- Eyebrows -->
    {eyebrows_d}
    <!-- Eyes -->
    {eyes_svg}
    <!-- Nose -->
    <path d="{nose_d}" stroke="{neck_color}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    <!-- Mouth -->
    <path d="{mouth_d}" stroke="{neck_color}" stroke-width="2" fill="none" stroke-linecap="round"/>
    {extra_svg}
  </g>
</svg>'''

def default_eyes(iris_color="#1E293B"):
    return f'''
    <ellipse cx="52" cy="51" rx="4.5" ry="4" fill="#fff"/>
    <circle cx="52" cy="51" r="2.8" fill="{iris_color}"/>
    <circle cx="53" cy="50" r="1" fill="#fff"/>
    <ellipse cx="68" cy="51" rx="4.5" ry="4" fill="#fff"/>
    <circle cx="68" cy="51" r="2.8" fill="{iris_color}"/>
    <circle cx="69" cy="50" r="1" fill="#fff"/>
    '''

def wink_eyes(iris_color="#1E293B"):
    return f'''
    <ellipse cx="52" cy="51" rx="4.5" ry="4" fill="#fff"/>
    <circle cx="52" cy="51" r="2.8" fill="{iris_color}"/>
    <circle cx="53" cy="50" r="1" fill="#fff"/>
    <path d="M64 51 Q68 47 72 51" stroke="{iris_color}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    '''

def glasses_svg():
    return '''
    <rect x="44" y="46" width="13" height="10" rx="3" fill="none" stroke="#1E293B" stroke-width="2"/>
    <rect x="63" y="46" width="13" height="10" rx="3" fill="none" stroke="#1E293B" stroke-width="2"/>
    <line x1="57" y1="51" x2="63" y2="51" stroke="#1E293B" stroke-width="1.8"/>
    <line x1="33" y1="50" x2="44" y2="50" stroke="#1E293B" stroke-width="1.8"/>
    <line x1="76" y1="50" x2="87" y2="50" stroke="#1E293B" stroke-width="1.8"/>
    '''

avatars = {}

# MALE 1 to 8
avatars["male_01.svg"] = create_svg(
    "#DBEAFE", "#BFDBFE", "#1D4ED8", "#7B4A32", "#6B3A2A", "#1C1917",
    '<ellipse cx="60" cy="31" rx="24" ry="10" fill="#1C1917"/><ellipse cx="40" cy="40" rx="10" ry="8" fill="#1C1917"/><ellipse cx="80" cy="40" rx="10" ry="8" fill="#1C1917"/>',
    '<path d="M48 45 Q54 42 58 45" stroke="#1C1917" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M62 45 Q66 42 72 45" stroke="#1C1917" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    default_eyes("#1C1917"), "M58 57 Q60 62 62 57", "M52 65 Q60 72 68 65"
)

avatars["male_02.svg"] = create_svg(
    "#FEF9C3", "#FEF08A", "#059669", "#FDDBB5", "#F5CBA7", "#D4A017",
    '<path d="M36 47 Q36 22 60 24 Q84 22 84 47 Q80 30 60 30 Q40 30 36 47Z" fill="#D4A017"/>',
    '<path d="M48 44 Q54 41 58 44" stroke="#A0740A" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q66 41 72 44" stroke="#A0740A" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#1E3A8A"), "M58 58 Q60 63 62 58", "M52 66 Q60 73 68 66", glasses_svg()
)

avatars["male_03.svg"] = create_svg(
    "#FCE7F3", "#FBCFE8", "#7C3AED", "#D4956A", "#C68642", "#111827",
    '<path d="M36 47 Q35 20 60 21 Q85 20 84 47 Q82 28 60 28 Q38 28 36 47Z" fill="#111827"/><path d="M44 70 Q60 80 76 70 Q76 75 60 77 Q44 75 44 70Z" fill="#111827" opacity="0.6"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#111827" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#111827" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    default_eyes("#3B1F0A"), "M58 57 Q60 62 62 57", "M51 65 Q60 72 69 65"
)

avatars["male_04.svg"] = create_svg(
    "#D1FAE5", "#A7F3D0", "#DC2626", "#FEECD5", "#FDE7CD", "#8B2500",
    '<path d="M36 47 Q34 18 60 20 Q86 18 84 47 Q82 26 60 26 Q38 26 36 47Z" fill="#8B2500"/><path d="M52 63 Q56 67 60 64 Q64 67 68 63 Q64 66 60 65 Q56 66 52 63Z" fill="#6B1C00" opacity="0.7"/>',
    '<path d="M47 44 Q53 41 57 44" stroke="#6B1C00" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M63 44 Q67 41 73 44" stroke="#6B1C00" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    default_eyes("#2F4F2F"), "M58 56 Q60 61 62 56", "M52 67 Q60 74 68 67"
)

avatars["male_05.svg"] = create_svg(
    "#E0E7FF", "#C7D2FE", "#374151", "#B5652A", "#A0522D", "#1A0A00",
    '<path d="M36 48 Q36 24 60 24 Q84 24 84 48 Q80 40 60 38 Q40 40 36 48Z" fill="#1A0A00"/><path d="M40 64 Q40 80 60 82 Q80 80 80 64 Q76 74 60 75 Q44 74 40 64Z" fill="#1A0A00" opacity="0.8"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#1A0A00" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#1A0A00" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    default_eyes("#1A0A00"), "M57 57 Q60 63 63 57", "M51 66 Q60 73 69 66"
)

avatars["male_06.svg"] = create_svg(
    "#FFF7ED", "#FED7AA", "#0891B2", "#FDDBB5", "#FAD5A5", "#111827",
    '<path d="M36 45 Q36 20 60 21 Q84 20 84 45 Q82 28 60 27 Q38 28 36 45Z" fill="#111827"/>',
    '<path d="M47 44 Q53 42 58 44" stroke="#111827" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 42 73 44" stroke="#111827" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#1A0A00"), "M58 57 Q60 62 62 57", "M52 65 Q60 71 68 65"
)

avatars["male_07.svg"] = create_svg(
    "#F3E8FF", "#E9D5FF", "#D97706", "#F3C598", "#E6B585", "#4B2E1E",
    '<path d="M34 45 Q34 21 60 22 Q86 21 86 45 Q80 27 60 27 Q40 27 34 45Z" fill="#4B2E1E"/><path d="M34 42 Q28 48 30 54 M86 42 Q92 48 90 54" stroke="#4B2E1E" stroke-width="4" fill="none"/>',
    '<path d="M47 43 Q53 40 58 43" stroke="#4B2E1E" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 40 73 43" stroke="#4B2E1E" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    wink_eyes("#4B2E1E"), "M58 57 Q60 62 62 57", "M52 65 Q60 72 68 65"
)

avatars["male_08.svg"] = create_svg(
    "#CCFBF1", "#99F6E4", "#2563EB", "#603813", "#4A2B0F", "#0F172A",
    '<ellipse cx="60" cy="30" rx="25" ry="12" fill="#0F172A"/><path d="M42 66 Q60 78 78 66 Q74 77 60 78 Q46 77 42 66Z" fill="#0F172A"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#0F172A" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#0F172A" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    default_eyes("#0F172A"), "M57 57 Q60 63 63 57", "M52 67 Q60 73 68 67", glasses_svg()
)

# FEMALE 1 to 8
avatars["female_01.svg"] = create_svg(
    "#FCE7F3", "#FBCFE8", "#EC4899", "#FDDBB5", "#FAD5A5", "#1C1917",
    '<path d="M30 45 Q30 18 60 19 Q90 18 90 45 L92 78 Q90 85 82 82 L80 50 Q78 28 60 28 Q42 28 40 50 L38 82 Q30 85 28 78Z" fill="#1C1917"/>',
    '<path d="M47 44 Q53 40 58 43" stroke="#1C1917" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 40 73 44" stroke="#1C1917" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#374151"), "M58 56 Q60 60 62 56", "M51 65 Q60 74 69 65",
    '<circle cx="60" cy="69" r="2.5" fill="#EF4444" opacity="0.3"/>'
)

avatars["female_02.svg"] = create_svg(
    "#DBEAFE", "#BFDBFE", "#2563EB", "#7B4A32", "#6B3A2A", "#1F2937",
    '<path d="M32 45 Q30 16 60 16 Q90 16 88 45 L90 85 Q82 88 80 55 Q78 26 60 26 Q42 26 40 55 L38 85 Q30 88 28 45Z" fill="#1F2937"/>',
    '<path d="M47 43 Q53 39 58 43" stroke="#1F2937" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 39 73 43" stroke="#1F2937" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#1F2937"), "M58 56 Q60 60 62 56", "M52 66 Q60 72 68 66"
)

avatars["female_03.svg"] = create_svg(
    "#FEF9C3", "#FEF08A", "#10B981", "#FEECD5", "#FDE7CD", "#D4A017",
    '<path d="M32 45 Q30 18 60 18 Q90 18 88 45 L92 82 Q82 85 80 55 Q78 28 60 28 Q42 28 40 55 L38 82 Q30 85 28 45Z" fill="#D4A017"/>',
    '<path d="M47 43 Q53 40 58 43" stroke="#A0740A" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 40 73 43" stroke="#A0740A" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#047857"), "M58 56 Q60 61 62 56", "M52 66 Q60 73 68 66"
)

avatars["female_04.svg"] = create_svg(
    "#E0E7FF", "#C7D2FE", "#8B5CF6", "#D4956A", "#C68642", "#3B1F0A",
    '<path d="M30 45 Q30 15 60 16 Q90 15 90 45 L94 85 Q80 88 80 55 Q78 27 60 27 Q42 27 40 55 L36 85 Q26 88 26 45Z" fill="#3B1F0A"/>',
    '<path d="M47 43 Q53 39 58 43" stroke="#3B1F0A" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 39 73 43" stroke="#3B1F0A" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#3B1F0A"), "M58 56 Q60 61 62 56", "M51 65 Q60 73 69 65", glasses_svg()
)

avatars["female_05.svg"] = create_svg(
    "#FFF7ED", "#FED7AA", "#F97316", "#F3C598", "#E6B585", "#8B2500",
    '<circle cx="60" cy="24" r="14" fill="#8B2500"/><path d="M36 45 Q36 24 60 25 Q84 24 84 45 Q80 32 60 32 Q40 32 36 45Z" fill="#8B2500"/>',
    '<path d="M47 43 Q53 40 58 43" stroke="#6B1C00" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 40 73 43" stroke="#6B1C00" stroke-width="2" fill="none" stroke-linecap="round"/>',
    wink_eyes("#6B1C00"), "M58 56 Q60 61 62 56", "M52 65 Q60 73 68 65"
)

avatars["female_06.svg"] = create_svg(
    "#D1FAE5", "#A7F3D0", "#06B6D4", "#A0522D", "#8B4513", "#111827",
    '<path d="M28 45 Q26 15 60 15 Q94 15 92 45 L94 88 Q82 90 80 58 Q78 28 60 28 Q42 28 40 58 L36 90 Q26 88 24 45Z" fill="#111827"/>',
    '<path d="M47 43 Q53 39 58 43" stroke="#111827" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 39 73 43" stroke="#111827" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    default_eyes("#111827"), "M57 57 Q60 62 63 57", "M52 66 Q60 73 68 66"
)

avatars["female_07.svg"] = create_svg(
    "#F3E8FF", "#E9D5FF", "#6366F1", "#FDDBB5", "#FAD5A5", "#4A0E17",
    '<path d="M32 45 Q30 18 60 18 Q90 18 88 45 L90 78 Q82 82 80 52 Q78 28 60 28 Q42 28 40 52 L38 78 Q30 82 28 45Z" fill="#4A0E17"/>',
    '<path d="M47 43 Q53 40 58 43" stroke="#4A0E17" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 40 73 43" stroke="#4A0E17" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#4A0E17"), "M58 56 Q60 60 62 56", "M52 66 Q60 72 68 66"
)

avatars["female_08.svg"] = create_svg(
    "#CCFBF1", "#99F6E4", "#14B8A6", "#603813", "#4A2B0F", "#0F172A",
    '<path d="M28 45 Q26 15 60 15 Q94 15 92 45 L94 88 Q82 90 80 58 Q78 28 60 28 Q42 28 40 58 L36 90 Q26 88 24 45Z" fill="#0F172A"/>',
    '<path d="M47 43 Q53 39 58 43" stroke="#0F172A" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M62 43 Q67 39 73 43" stroke="#0F172A" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
    default_eyes("#0F172A"), "M57 57 Q60 62 63 57", "M52 66 Q60 73 68 66"
)

# NEUTRAL 1 to 8
avatars["neutral_01.svg"] = create_svg(
    "#E2E8F0", "#CBD5E1", "#475569", "#FDDBB5", "#FAD5A5", "#334155",
    '<path d="M38 45 Q38 22 60 23 Q82 22 82 45 Q78 30 60 30 Q42 30 38 45Z" fill="#334155"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#334155" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#334155" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#334155"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_02.svg"] = create_svg(
    "#FEF3C7", "#FDE68A", "#D97706", "#7B4A32", "#6B3A2A", "#1C1917",
    '<path d="M38 45 Q38 22 60 23 Q82 22 82 45 Q78 30 60 30 Q42 30 38 45Z" fill="#1C1917"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#1C1917" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#1C1917" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#1C1917"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_03.svg"] = create_svg(
    "#F3E8FF", "#E9D5FF", "#9333EA", "#D4956A", "#C68642", "#2E1065",
    '<path d="M36 45 Q36 20 60 21 Q84 20 84 45 Q80 28 60 28 Q40 28 36 45Z" fill="#2E1065"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#2E1065" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#2E1065" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#2E1065"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66", glasses_svg()
)

avatars["neutral_04.svg"] = create_svg(
    "#DCFCE7", "#BBF7D0", "#16A34A", "#FEECD5", "#FDE7CD", "#B45309",
    '<path d="M36 45 Q36 20 60 21 Q84 20 84 45 Q80 28 60 28 Q40 28 36 45Z" fill="#B45309"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#B45309" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#B45309" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#B45309"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_05.svg"] = create_svg(
    "#FFE4E6", "#FECDD3", "#E11D48", "#A0522D", "#8B4513", "#111827",
    '<path d="M38 45 Q38 22 60 23 Q82 22 82 45 Q78 30 60 30 Q42 30 38 45Z" fill="#111827"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#111827" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#111827" stroke-width="2" fill="none" stroke-linecap="round"/>',
    wink_eyes("#111827"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_06.svg"] = create_svg(
    "#E0F2FE", "#BAE6FD", "#0284C7", "#603813", "#4A2B0F", "#0F172A",
    '<path d="M38 45 Q38 22 60 23 Q82 22 82 45 Q78 30 60 30 Q42 30 38 45Z" fill="#0F172A"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#0F172A" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#0F172A" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#0F172A"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_07.svg"] = create_svg(
    "#F1F5F9", "#E2E8F0", "#0F172A", "#F3C598", "#E6B585", "#78350F",
    '<path d="M36 45 Q36 20 60 21 Q84 20 84 45 Q80 28 60 28 Q40 28 36 45Z" fill="#78350F"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#78350F" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#78350F" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#78350F"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66"
)

avatars["neutral_08.svg"] = create_svg(
    "#FAF5FF", "#F3E8FF", "#7E22CE", "#FDDBB5", "#FAD5A5", "#18181B",
    '<path d="M36 45 Q36 20 60 21 Q84 20 84 45 Q80 28 60 28 Q40 28 36 45Z" fill="#18181B"/>',
    '<path d="M47 44 Q53 41 58 44" stroke="#18181B" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M62 44 Q67 41 73 44" stroke="#18181B" stroke-width="2" fill="none" stroke-linecap="round"/>',
    default_eyes("#18181B"), "M58 57 Q60 61 62 57", "M52 66 Q60 72 68 66", glasses_svg()
)

for filename, content in avatars.items():
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(avatars)} SVGs in {AVATAR_DIR}")
