import os

avatar_dir = os.path.join(os.path.dirname(__file__), "static", "images", "avatars")
os.makedirs(avatar_dir, exist_ok=True)

def build_svg(bg_color, skin_color, hair_color, clothing_color, features_svg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
  <defs>
    <clipPath id="avatar-clip">
      <circle cx="60" cy="60" r="54" />
    </clipPath>
  </defs>
  <!-- Circle Background -->
  <circle cx="60" cy="60" r="54" fill="{bg_color}" />
  
  <g clip-path="url(#avatar-clip)">
    <!-- Base Body & Neck -->
    <path d="M44 80 L44 68 Q44 62 60 62 Q76 62 76 68 L76 80 Z" fill="{skin_color}" />
    <!-- Shoulders / Clothing -->
    <path d="M20 115 Q20 85 60 85 Q100 85 100 115 Z" fill="{clothing_color}" />
    <!-- Head -->
    <ellipse cx="60" cy="52" rx="22" ry="25" fill="{skin_color}" />
    <!-- Ears -->
    <circle cx="37" cy="52" r="4" fill="{skin_color}" />
    <circle cx="83" cy="52" r="4" fill="{skin_color}" />
    <!-- Eyes -->
    <circle cx="51" cy="50" r="2.5" fill="#2D3748" />
    <circle cx="69" cy="50" r="2.5" fill="#2D3748" />
    <!-- Eyebrows -->
    <path d="M47 44 Q51 42 55 44" stroke="#2D3748" stroke-width="2" stroke-linecap="round" fill="none" />
    <path d="M65 44 Q69 42 73 44" stroke="#2D3748" stroke-width="2" stroke-linecap="round" fill="none" />
    <!-- Smile -->
    <path d="M54 62 Q60 67 66 62" stroke="#2D3748" stroke-width="2" stroke-linecap="round" fill="none" />
    {features_svg}
  </g>
</svg>'''

avatars_data = [
    # MALE AVATARS
    ("male_01.svg", "#E0F2FE", "#F1C27D", "#2563EB", "#1E293B",
     '''<path d="M37 45 Q38 25 60 25 Q82 25 83 45 Q75 32 60 32 Q45 32 37 45 Z" fill="#1E293B" />
     <circle cx="51" cy="50" r="7" stroke="#0F172A" stroke-width="2" fill="none" />
     <circle cx="69" cy="50" r="7" stroke="#0F172A" stroke-width="2" fill="none" />
     <line x1="58" y1="50" x2="62" y2="50" stroke="#0F172A" stroke-width="2" />'''),

    ("male_02.svg", "#FEE2E2", "#E0AC69", "#DC2626", "#451A03",
     '''<circle cx="50" cy="27" r="10" fill="#451A03" />
     <circle cx="60" cy="25" r="11" fill="#451A03" />
     <circle cx="70" cy="27" r="10" fill="#451A03" />
     <path d="M38 40 C36 30 45 28 60 28 C75 28 84 30 82 40 Z" fill="#451A03" />
     <path d="M40 55 C40 73 50 78 60 78 C70 78 80 73 80 55 C74 65 46 65 40 55 Z" fill="#451A03" />'''),

    ("male_03.svg", "#FEF3C7", "#8D5524", "#D97706", "#171717",
     '''<path d="M38 42 C38 25 50 22 60 22 C70 22 82 25 82 42 Q78 30 60 30 Q42 30 38 42 Z" fill="#171717" />
     <rect x="42" y="45" width="16" height="10" rx="3" fill="#171717" />
     <rect x="62" y="45" width="16" height="10" rx="3" fill="#171717" />
     <line x1="58" y1="48" x2="62" y2="48" stroke="#171717" stroke-width="2" />'''),

    ("male_04.svg", "#ECFDF5", "#FFDBAC", "#059669", "#B45309",
     '''<path d="M36 45 C35 25 45 22 55 22 C75 22 84 30 84 45 Q70 28 55 30 Q40 32 36 45 Z" fill="#B45309" />
     <path d="M52 64 Q60 62 68 64 Q68 73 60 74 Q52 73 52 64 Z" fill="#B45309" />'''),

    ("male_05.svg", "#F3E8FF", "#5C3818", "#7C3AED", "#09090B",
     '''<rect x="36" y="24" width="6" height="30" rx="3" fill="#09090B" />
     <rect x="44" y="20" width="6" height="35" rx="3" fill="#09090B" />
     <rect x="52" y="18" width="6" height="38" rx="3" fill="#09090B" />
     <rect x="60" y="18" width="6" height="38" rx="3" fill="#09090B" />
     <rect x="68" y="20" width="6" height="35" rx="3" fill="#09090B" />
     <rect x="76" y="24" width="6" height="30" rx="3" fill="#09090B" />
     <path d="M44 60 C44 72 52 75 60 75 C68 75 76 72 76 60 C70 68 50 68 44 60 Z" fill="#09090B" opacity="0.3" />'''),

    ("male_06.svg", "#CCFBF1", "#F1C27D", "#0D9488", "#78350F",
     '''<path d="M37 45 C37 28 46 25 60 25 C74 25 83 28 83 45 Z" fill="#78350F" opacity="0.8" />
     <rect x="42" y="44" width="15" height="12" rx="2" stroke="#0F172A" stroke-width="2" fill="none" />
     <rect x="63" y="44" width="15" height="12" rx="2" stroke="#0F172A" stroke-width="2" fill="none" />
     <line x1="57" y1="49" x2="63" y2="49" stroke="#0F172A" stroke-width="2" />'''),

    ("male_07.svg", "#FFF7ED", "#C68642", "#EA580C", "#1C1917",
     '''<path d="M45 30 Q60 24 75 30" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.5" />
     <path d="M48 60 Q60 56 72 60 Q60 64 48 60 Z" fill="#1C1917" />'''),

    ("male_08.svg", "#F0FDF4", "#E0AC69", "#16A34A", "#292524",
     '''<path d="M36 42 Q40 18 60 18 Q80 20 84 40 Q75 28 60 26 Q42 28 36 42 Z" fill="#292524" />
     <path d="M50 85 L60 102 L70 85" fill="#FFFFFF" />
     <path d="M57 95 L60 115 L63 95 Z" fill="#DC2626" />'''),

    # FEMALE AVATARS
    ("female_01.svg", "#FCE7F3", "#FFDBAC", "#DB2777", "#B45309",
     '''<path d="M34 50 C32 25 45 20 60 20 C75 20 88 25 86 50 C88 65 82 85 78 95 C75 85 80 60 78 45 C70 30 50 30 42 45 C40 60 45 85 42 95 C38 85 32 65 34 50 Z" fill="#B45309" />'''),

    ("female_02.svg", "#E0F2FE", "#E0AC69", "#0284C7", "#09090B",
     '''<path d="M35 50 C34 25 45 20 60 20 C75 20 86 25 85 50 C86 65 80 70 78 72 C78 50 75 30 60 30 C45 30 42 50 42 72 C40 70 34 65 35 50 Z" fill="#09090B" />
     <circle cx="51" cy="50" r="7" stroke="#0284C7" stroke-width="2" fill="none" />
     <circle cx="69" cy="50" r="7" stroke="#0284C7" stroke-width="2" fill="none" />
     <line x1="58" y1="50" x2="62" y2="50" stroke="#0284C7" stroke-width="2" />'''),

    ("female_03.svg", "#FEF2F2", "#5C3818", "#E11D48", "#171717",
     '''<circle cx="60" cy="38" r="28" fill="#171717" />
     <ellipse cx="60" cy="52" rx="22" ry="25" fill="#5C3818" />
     <circle cx="34" cy="56" r="5" stroke="#F59E0B" stroke-width="2" fill="none" />
     <circle cx="86" cy="56" r="5" stroke="#F59E0B" stroke-width="2" fill="none" />'''),

    ("female_04.svg", "#F0FDFA", "#F1C27D", "#0D9488", "#451A03",
     '''<circle cx="60" cy="18" r="10" fill="#451A03" />
     <path d="M60 18 Q78 15 82 32 Q72 28 60 22 Z" fill="#451A03" />
     <path d="M36 45 C35 25 45 22 60 22 C75 22 84 25 84 45 Q75 30 60 30 Q45 30 36 45 Z" fill="#451A03" />'''),

    ("female_05.svg", "#FFFBEB", "#8D5524", "#D97706", "#292524",
     '''<circle cx="36" cy="45" r="9" fill="#292524" />
     <circle cx="34" cy="58" r="9" fill="#292524" />
     <circle cx="36" cy="70" r="8" fill="#292524" />
     <circle cx="84" cy="45" r="9" fill="#292524" />
     <circle cx="86" cy="58" r="9" fill="#292524" />
     <circle cx="84" cy="70" r="8" fill="#292524" />
     <path d="M37 42 C37 25 46 22 60 22 C74 22 83 25 83 42 Z" fill="#292524" />'''),

    ("female_06.svg", "#F5F3FF", "#FFDBAC", "#8B5CF6", "#7C2D12",
     '''<path d="M36 46 C35 28 45 22 60 22 C75 22 84 28 84 40 C75 32 68 32 60 34 C50 32 42 38 36 46 Z" fill="#7C2D12" />
     <path d="M43 45 Q51 43 57 49 Q51 53 43 49 Z" stroke="#4C1D95" stroke-width="2" fill="none" />
     <path d="M63 49 Q69 43 77 45 Q77 49 69 53 Z" stroke="#4C1D95" stroke-width="2" fill="none" />'''),

    ("female_07.svg", "#ECFDF5", "#C68642", "#10B981", "#064E3B",
     '''<circle cx="60" cy="20" r="9" fill="#064E3B" />
     <path d="M38 45 C37 28 46 25 60 25 C74 25 83 28 83 45 Q72 32 60 32 Q48 32 38 45 Z" fill="#064E3B" />'''),

    ("female_08.svg", "#EFF6FF", "#E0AC69", "#3B82F6", "#78350F",
     '''<path d="M36 32 Q60 24 84 32" stroke="#78350F" stroke-width="6" stroke-linecap="round" fill="none" />
     <path d="M36 48 C35 30 45 25 60 25 C75 25 84 30 84 48 C84 68 80 88 76 95 Q80 70 78 50 C70 35 50 35 42 50 Q40 70 44 95 C40 88 36 68 36 48 Z" fill="#78350F" />'''),

    # NEUTRAL AVATARS
    ("neutral_01.svg", "#F1F5F9", "#F8D7DA", "#64748B", "#475569",
     '''<path d="M37 45 C36 28 46 23 60 23 C74 23 84 28 83 45 Q72 32 60 32 Q48 32 37 45 Z" fill="#475569" />
     <path d="M34 42 Q60 20 86 42 L86 46 Q60 38 34 46 Z" fill="#334155" />'''),

    ("neutral_02.svg", "#F0F9FF", "#E0AC69", "#0EA5E9", "#0369A1",
     '''<path d="M30 65 Q30 20 60 20 Q90 20 90 65 Q90 95 60 95 Q30 95 30 65 Z" fill="#0EA5E9" />
     <ellipse cx="60" cy="54" rx="20" ry="23" fill="#E0AC69" />
     <circle cx="51" cy="52" r="2.5" fill="#2D3748" />
     <circle cx="69" cy="52" r="2.5" fill="#2D3748" />
     <path d="M54 63 Q60 67 66 63" stroke="#2D3748" stroke-width="2" stroke-linecap="round" fill="none" />'''),

    ("neutral_03.svg", "#FEF3C7", "#FFDBAC", "#F59E0B", "#78350F",
     '''<path d="M36 45 C36 26 46 22 60 22 C74 22 84 26 84 45 Q72 30 60 30 Q48 30 36 45 Z" fill="#78350F" />
     <circle cx="51" cy="50" r="8" fill="#F59E0B" opacity="0.3" stroke="#B45309" stroke-width="2" />
     <circle cx="69" cy="50" r="8" fill="#F59E0B" opacity="0.3" stroke="#B45309" stroke-width="2" />
     <line x1="59" y1="50" x2="61" y2="50" stroke="#B45309" stroke-width="2" />'''),

    ("neutral_04.svg", "#F3E8FF", "#C68642", "#A855F7", "#581C87",
     '''<path d="M35 48 C34 26 45 22 60 22 C75 22 86 26 85 48 C85 62 82 75 78 82 C76 68 76 48 60 40 C44 48 44 68 42 82 C38 75 35 62 35 48 Z" fill="#581C87" />'''),

    ("neutral_05.svg", "#E0FAFF", "#F1C27D", "#06B6D4", "#164E63",
     '''<path d="M32 40 Q60 22 88 40 L94 44 Q60 38 26 44 Z" fill="#164E63" />
     <circle cx="51" cy="50" r="7" stroke="#164E63" stroke-width="2" fill="none" />
     <circle cx="69" cy="50" r="7" stroke="#164E63" stroke-width="2" fill="none" />
     <line x1="58" y1="50" x2="62" y2="50" stroke="#164E63" stroke-width="2" />'''),

    ("neutral_06.svg", "#ECFDF5", "#8D5524", "#10B981", "#064E3B",
     '''<path d="M35 50 C34 25 45 20 60 20 C75 20 86 25 85 50 L85 65 L76 60 Q76 42 60 42 Q44 42 44 60 L35 65 Z" fill="#064E3B" />'''),

    ("neutral_07.svg", "#FFF1F2", "#5C3818", "#F43F5E", "#881337",
     '''<circle cx="60" cy="20" r="8" fill="#881337" />
     <path d="M37 45 C36 28 46 25 60 25 C74 25 84 28 83 45 Q72 32 60 32 Q48 32 37 45 Z" fill="#881337" />'''),

    ("neutral_08.svg", "#F8FAFC", "#94A3B8", "#475569", "#0F172A",
     '''<rect x="38" y="28" width="44" height="48" rx="14" fill="#334155" />
     <rect x="44" y="34" width="32" height="22" rx="6" fill="#0F172A" />
     <circle cx="52" cy="45" r="4" fill="#38BDF8" />
     <circle cx="68" cy="45" r="4" fill="#38BDF8" />
     <path d="M53 62 Q60 66 67 62" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" fill="none" />''')
]

for filename, bg, skin, clothing, hair, features in avatars_data:
    content = build_svg(bg, skin, hair, clothing, features)
    with open(os.path.join(avatar_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(avatars_data)} SVG avatars.")
