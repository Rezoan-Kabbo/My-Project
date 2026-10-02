"""
ui/theme.py
-----------
Consistent visual themes, colors, button styles, and Matplotlib axis styling
for Morse Signal Lab.
"""

from typing import Dict, Any, Tuple
import customtkinter as ctk

# UI Theme Color Palettes for Matplotlib Plots
THEME_LIGHT: Dict[str, str] = {
    'fig_bg': '#f8fafc',
    'ax_bg': '#ffffff',
    'text': '#334155',
    'grid': '#e2e8f0',
    'spine': '#cbd5e1',
    'clean': '#0284c7',
    'fft': '#e11d48',
    'noisy': '#d97706',
    'filtered': '#059669',
    'mic': '#7c3aed',
    'env': '#0284c7',
    'thresh': '#dc2626',
    'response': '#9333ea'
}

THEME_DARK: Dict[str, str] = {
    'fig_bg': '#1e212b',
    'ax_bg': '#14161f',
    'text': '#94a3b8',
    'grid': '#2d3345',
    'spine': '#3b4256',
    'clean': '#38bdf8',
    'fft': '#fb7185',
    'noisy': '#fbbf24',
    'filtered': '#34d399',
    'mic': '#c084fc',
    'env': '#38bdf8',
    'thresh': '#f43f5e',
    'response': '#c084fc'
}

# ----------------------------------------------------------------------
# Standardized Modern UI Button Accents (Light, Dark)
# ----------------------------------------------------------------------

# Primary Brand Action (Hero button on each tab)
BTN_PRIMARY: Tuple[str, str] = ("#2563eb", "#1d4ed8")
BTN_PRIMARY_HOVER: Tuple[str, str] = ("#1d4ed8", "#1e40af")

# Media Playback (Play / Listen)
BTN_PLAY: Tuple[str, str] = ("#10b981", "#059669")
BTN_PLAY_HOVER: Tuple[str, str] = ("#059669", "#047857")

# Media Stop
BTN_STOP: Tuple[str, str] = ("#ef4444", "#dc2626")
BTN_STOP_HOVER: Tuple[str, str] = ("#dc2626", "#b91c1c")

# Secondary / Neutral (Clean, modern low-contrast surface)
BTN_SECONDARY: Tuple[str, str] = ("#e2e8f0", "#282c37")
BTN_SECONDARY_HOVER: Tuple[str, str] = ("#cbd5e1", "#3b4256")
BTN_SECONDARY_TEXT: Tuple[str, str] = ("#1e293b", "#f1f5f9")

# Inter-tab Transfer / Routing (Unified modern indigo pill)
BTN_TRANSFER: Tuple[str, str] = ("#ede9fe", "#261a45")
BTN_TRANSFER_HOVER: Tuple[str, str] = ("#ddd6fe", "#352461")
BTN_TRANSFER_TEXT: Tuple[str, str] = ("#4338ca", "#c7d2fe")

# Action / Warning Accent
BTN_ACTION: Tuple[str, str] = ("#6366f1", "#4f46e5")
BTN_ACTION_HOVER: Tuple[str, str] = ("#4f46e5", "#4338ca")
BTN_WARN: Tuple[str, str] = ("#d97706", "#b45309")
BTN_WARN_HOVER: Tuple[str, str] = ("#b45309", "#92400e")

# Standard Dimensions
BTN_HEIGHT_LG = 32
BTN_HEIGHT_MD = 28
BTN_HEIGHT_SM = 22
BTN_RADIUS = 6
BTN_RADIUS_PILL = 12
BTN_CHIP_RADIUS = 12


def get_plot_theme() -> Dict[str, str]:
    """Returns color tokens for Matplotlib matching the active CustomTkinter mode."""
    mode = ctk.get_appearance_mode()
    return THEME_LIGHT if mode == "Light" else THEME_DARK


def style_axis(
    ax: Any,
    colors: Dict[str, str],
    title: str = "",
    xlabel: str = "",
    ylabel: str = ""
) -> None:
    """Consistently styles a Matplotlib axes instance to blend with CustomTkinter."""
    ax.set_facecolor(colors['ax_bg'])
    if title:
        ax.set_title(title, color=colors['text'], fontsize=10, pad=6, weight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, color=colors['text'], fontsize=8)
    if ylabel:
        ax.set_ylabel(ylabel, color=colors['text'], fontsize=8)
    ax.tick_params(colors=colors['text'], labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.35, color=colors['grid'])
    for spine in ax.spines.values():
        spine.set_color(colors['spine'])
