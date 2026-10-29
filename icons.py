_PATHS = {
    "chart-column": (
        '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/>'
        '<path d="M13 17V5"/><path d="M8 17v-3"/>'
    ),
    "trophy": (
        '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
        '<path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
        '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
        '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "settings-2": (
        '<path d="M20 7h-9"/><path d="M14 17H5"/>'
        '<circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>'
    ),
}


def icon(name, size=24, stroke_width=2):
    # Restituisce l'SVG inline dell'icona; il colore segue "color" del contenitore.
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_PATHS[name]}</svg>'
    )
