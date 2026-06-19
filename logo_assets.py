# REDROB AI Brand & Logo Assets

# Custom-designed geometric "R" Monogram SVG Mark
MONOGRAM_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
  <defs>
    <!-- Dark Mode Gradients -->
    <linearGradient id="rGradDark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3B82F6"/> <!-- Electric Blue -->
      <stop offset="50%" stop-color="#06B6D4"/> <!-- Cyan -->
      <stop offset="100%" stop-color="#8B5CF6"/> <!-- Purple -->
    </linearGradient>
    <!-- Glowing Drop Shadows -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  
  <!-- Network Connections (Lines) -->
  <line x1="25" y1="20" x2="25" y2="80" stroke="#334155" stroke-width="1.5" stroke-dasharray="2,2"/>
  <line x1="25" y1="20" x2="65" y2="20" stroke="#334155" stroke-width="1.5"/>
  <line x1="65" y1="20" x2="65" y2="50" stroke="#334155" stroke-width="1.5"/>
  <line x1="65" y1="50" x2="25" y2="50" stroke="#334155" stroke-width="1.5"/>
  <line x1="25" y1="50" x2="70" y2="80" stroke="#334155" stroke-width="1.5" stroke-dasharray="3,3"/>
  <line x1="65" y1="20" x2="45" y2="50" stroke="#334155" stroke-width="1" opacity="0.5"/>
  
  <!-- Left Vertical Ranking Layers (Pillars) -->
  <rect x="22" y="20" width="6" height="15" rx="3" fill="url(#rGradDark)" opacity="0.8"/>
  <rect x="22" y="40" width="6" height="15" rx="3" fill="url(#rGradDark)" opacity="0.95"/>
  <rect x="22" y="60" width="6" height="20" rx="3" fill="url(#rGradDark)"/>
  
  <!-- Outer Loop Curve (Neural Net Paths) -->
  <path d="M28,27.5 C55,27.5 70,35 60,45 C52,51 28,47.5 28,47.5" fill="none" stroke="url(#rGradDark)" stroke-width="5" stroke-linecap="round"/>
  
  <!-- Diagonal Leg (Search Traversal Graph) -->
  <path d="M38,47.5 L67,78" fill="none" stroke="url(#rGradDark)" stroke-width="5" stroke-linecap="round"/>
  
  <!-- Search Intelligence Target/Lens (Neural Center) -->
  <circle cx="48" cy="38" r="8" fill="none" stroke="#06B6D4" stroke-width="1.5" stroke-dasharray="1.5,1.5"/>
  <circle cx="48" cy="38" r="3" fill="#10B981" filter="url(#glow)"/>
  
  <!-- Neural Network Nodes (Circles) -->
  <circle cx="25" cy="20" r="4.5" fill="#020617" stroke="#3B82F6" stroke-width="2"/>
  <circle cx="65" cy="20" r="4.5" fill="#020617" stroke="#06B6D4" stroke-width="2"/>
  <circle cx="60" cy="45" r="4.5" fill="#020617" stroke="#8B5CF6" stroke-width="2"/>
  <circle cx="25" cy="50" r="4.5" fill="#020617" stroke="#10B981" stroke-width="2"/>
  <circle cx="70" cy="80" r="4.5" fill="#020617" stroke="#3B82F6" stroke-width="2"/>
  <circle cx="25" cy="80" r="4.5" fill="#020617" stroke="#8B5CF6" stroke-width="2"/>
</svg>
"""

# Horizontal Full Logo - Dark Mode
LOGO_DARK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 60" width="100%" height="100%">
  <defs>
    <linearGradient id="rGradD" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" fill="#3B82F6" stop-color="#3B82F6"/>
      <stop offset="50%" fill="#06B6D4" stop-color="#06B6D4"/>
      <stop offset="100%" fill="#8B5CF6" stop-color="#8B5CF6"/>
    </linearGradient>
  </defs>
  <!-- Monogram embedded -->
  <g transform="translate(5, -10) scale(0.8)">
    <line x1="25" y1="20" x2="25" y2="80" stroke="#334155" stroke-width="1.5" stroke-dasharray="2,2"/>
    <line x1="25" y1="20" x2="65" y2="20" stroke="#334155" stroke-width="1.5"/>
    <line x1="65" y1="20" x2="65" y2="50" stroke="#334155" stroke-width="1.5"/>
    <line x1="65" y1="50" x2="25" y2="50" stroke="#334155" stroke-width="1.5"/>
    <line x1="25" y1="50" x2="70" y2="80" stroke="#334155" stroke-width="1.5"/>
    <rect x="22" y="20" width="6" height="15" rx="3" fill="url(#rGradD)" opacity="0.8"/>
    <rect x="22" y="40" width="6" height="15" rx="3" fill="url(#rGradD)" opacity="0.95"/>
    <rect x="22" y="60" width="6" height="20" rx="3" fill="url(#rGradD)"/>
    <path d="M28,27.5 C55,27.5 70,35 60,45 C52,51 28,47.5 28,47.5" fill="none" stroke="url(#rGradD)" stroke-width="5" stroke-linecap="round"/>
    <path d="M38,47.5 L67,78" fill="none" stroke="url(#rGradD)" stroke-width="5" stroke-linecap="round"/>
    <circle cx="48" cy="38" r="8" fill="none" stroke="#06B6D4" stroke-width="1.5" stroke-dasharray="1.5,1.5"/>
    <circle cx="48" cy="38" r="3" fill="#10B981"/>
    <circle cx="25" cy="20" r="4.5" fill="#020617" stroke="#3B82F6" stroke-width="2"/>
    <circle cx="65" cy="20" r="4.5" fill="#020617" stroke="#06B6D4" stroke-width="2"/>
    <circle cx="60" cy="45" r="4.5" fill="#020617" stroke="#8B5CF6" stroke-width="2"/>
    <circle cx="25" cy="50" r="4.5" fill="#020617" stroke="#10B981" stroke-width="2"/>
    <circle cx="70" cy="80" r="4.5" fill="#020617" stroke="#3B82F6" stroke-width="2"/>
    <circle cx="25" cy="80" r="4.5" fill="#020617" stroke="#8B5CF6" stroke-width="2"/>
  </g>
  
  <!-- Text Styling -->
  <text x="80" y="32" font-family="'Inter', sans-serif" font-weight="800" font-size="22" fill="#FFFFFF" letter-spacing="1">REDROB</text>
  <text x="80" y="48" font-family="'Inter', sans-serif" font-weight="600" font-size="10" fill="#94A3B8" letter-spacing="2">AI TALENT INTELLIGENCE</text>
</svg>
"""

# Horizontal Full Logo - Light Mode
LOGO_LIGHT_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 60" width="100%" height="100%">
  <defs>
    <linearGradient id="rGradL" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" fill="#2563EB" stop-color="#2563EB"/>
      <stop offset="50%" fill="#06B6D4" stop-color="#06B6D4"/>
      <stop offset="100%" fill="#7C3AED" stop-color="#7C3AED"/>
    </linearGradient>
  </defs>
  <!-- Monogram embedded with white background nodes -->
  <g transform="translate(5, -10) scale(0.8)">
    <line x1="25" y1="20" x2="25" y2="80" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="2,2"/>
    <line x1="25" y1="20" x2="65" y2="20" stroke="#CBD5E1" stroke-width="1.5"/>
    <line x1="65" y1="20" x2="65" y2="50" stroke="#CBD5E1" stroke-width="1.5"/>
    <line x1="65" y1="50" x2="25" y2="50" stroke="#CBD5E1" stroke-width="1.5"/>
    <line x1="25" y1="50" x2="70" y2="80" stroke="#CBD5E1" stroke-width="1.5"/>
    <rect x="22" y="20" width="6" height="15" rx="3" fill="url(#rGradL)" opacity="0.8"/>
    <rect x="22" y="40" width="6" height="15" rx="3" fill="url(#rGradL)" opacity="0.95"/>
    <rect x="22" y="60" width="6" height="20" rx="3" fill="url(#rGradL)"/>
    <path d="M28,27.5 C55,27.5 70,35 60,45 C52,51 28,47.5 28,47.5" fill="none" stroke="url(#rGradL)" stroke-width="5" stroke-linecap="round"/>
    <path d="M38,47.5 L67,78" fill="none" stroke="url(#rGradL)" stroke-width="5" stroke-linecap="round"/>
    <circle cx="48" cy="38" r="8" fill="none" stroke="#06B6D4" stroke-width="1.5" stroke-dasharray="1.5,1.5"/>
    <circle cx="48" cy="38" r="3" fill="#10B981"/>
    <circle cx="25" cy="20" r="4.5" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="65" cy="20" r="4.5" fill="#FFFFFF" stroke="#06B6D4" stroke-width="2"/>
    <circle cx="60" cy="45" r="4.5" fill="#FFFFFF" stroke="#7C3AED" stroke-width="2"/>
    <circle cx="25" cy="50" r="4.5" fill="#FFFFFF" stroke="#10B981" stroke-width="2"/>
    <circle cx="70" cy="80" r="4.5" fill="#FFFFFF" stroke="#2563EB" stroke-width="2"/>
    <circle cx="25" cy="80" r="4.5" fill="#FFFFFF" stroke="#7C3AED" stroke-width="2"/>
  </g>
  
  <!-- Text Styling -->
  <text x="80" y="32" font-family="'Inter', sans-serif" font-weight="800" font-size="22" fill="#0F172A" letter-spacing="1">REDROB</text>
  <text x="80" y="48" font-family="'Inter', sans-serif" font-weight="600" font-size="10" fill="#475569" letter-spacing="2">AI TALENT INTELLIGENCE</text>
</svg>
"""

# Favicon SVG base64 helper template
FAVICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="32" height="32">
  <defs>
    <linearGradient id="fGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" fill="#3B82F6" stop-color="#3B82F6"/>
      <stop offset="100%" fill="#8B5CF6" stop-color="#8B5CF6"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="20" fill="#0F172A"/>
  <path d="M35,25 H55 C65,25 70,30 65,40 C60,45 50,45 50,45 L70,75 M35,25 V75" fill="none" stroke="url(#fGrad)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""
