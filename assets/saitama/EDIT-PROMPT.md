# Transparent cutout edit

Tool: built-in `image_gen.imagegen` in edit mode, with `transparent_background: true`.

Input: the option C illustration shown in the character comparison, downloaded from the PNGWing source credited in [CREDITS.md](./CREDITS.md).

Final prompt:

> Use case: background-extraction. Input image 1 is the edit target: the exact existing chibi Saitama illustration chosen by the user. Remove only the gray and white checkerboard background around the character and replace it with actual transparent alpha. Preserve the existing character exactly: same bored deadpan face, bald head, thick black outlines, red gloves and boots, yellow jumpsuit, white/blue-gray cape, shading, highlights, stance, proportions and silhouette. Preserve the white sticker outline around the character. Do not redraw, restyle, re-pose or add anything. Output the complete unchanged character on a genuinely transparent background, with no checkerboard, no floor, no shadow, no text. Match the input framing and aspect ratio.

Output: `chibi-saitama.png`. Character movement and shockwave effects are implemented in SVG by `scripts/generate_profile.py`.
