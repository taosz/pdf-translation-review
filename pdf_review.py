"""Create a local two-column PDF for manual translation review."""
from __future__ import annotations

import argparse
from copy import copy
from pathlib import Path
import sys

from pypdf import PdfReader, PdfWriter

MAX_BYTES = 50 * 1024 * 1024
MAX_PAGES = 200
CELL_WIDTH, CELL_HEIGHT, MARGIN = 612.0, 792.0, 18.0


class ReviewError(Exception):
    pass


def open_pdf(path: Path) -> PdfReader:
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ReviewError('Each input must be an existing, non-empty PDF of at most 50 MiB.')
    reader = PdfReader(path, strict=True)
    if reader.is_encrypted:
        raise ReviewError('Encrypted PDFs are not supported. Use an authorized accessible copy.')
    if not 1 <= len(reader.pages) <= MAX_PAGES:
        raise ReviewError('Each input must have between 1 and 200 pages.')
    return reader


def place(target, source, side: int) -> None:
    page = copy(source)
    # This is a visual reading copy, not an interactive PDF editor. Avoid
    # copying document-level interactive elements into the assembled pages.
    for key in ('/Annots', '/AA', '/B'):
        page.pop(key, None)
    if page.rotation:
        page.transfer_rotation_to_content()
    box = page.cropbox
    width, height = float(box.width), float(box.height)
    if width <= 0 or height <= 0:
        raise ReviewError('A source page has an invalid visible page box.')
    scale = min((CELL_WIDTH - MARGIN * 2) / width, (CELL_HEIGHT - MARGIN * 2) / height)
    x = side * CELL_WIDTH + (CELL_WIDTH - width * scale) / 2
    y = (CELL_HEIGHT - height * scale) / 2
    target.merge_transformed_page(page, (scale, 0, 0, scale,
                                       x - float(box.left) * scale,
                                       y - float(box.bottom) * scale))


def build(source: Path, translated: Path, output: Path, source_start=1, translated_start=1, count=None):
    if output.exists() or output.resolve() in {source.resolve(), translated.resolve()}:
        raise ReviewError('Output already exists or is an input. Choose a new output path.')
    first, second = open_pdf(source), open_pdf(translated)
    if source_start < 1 or translated_start < 1:
        raise ReviewError('Page numbers start at 1.')
    remaining_a = len(first.pages) - source_start + 1
    remaining_b = len(second.pages) - translated_start + 1
    if count is None:
        if remaining_a != remaining_b:
            raise ReviewError('The remaining page counts differ; use --pages to choose the number of pairs.')
        count = remaining_a
    if count < 1 or count > min(remaining_a, remaining_b):
        raise ReviewError('Requested page range is outside one or both PDFs.')
    writer = PdfWriter()
    for offset in range(count):
        page = writer.add_blank_page(width=CELL_WIDTH * 2, height=CELL_HEIGHT)
        place(page, first.pages[source_start - 1 + offset], 0)
        place(page, second.pages[translated_start - 1 + offset], 1)
    # Exclusive creation prevents overwrite; remove only a newly created file
    # if serialization fails. No input is deleted or overwritten.
    created = False
    try:
        with output.open('xb') as target:
            created = True
            writer.write(target)
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description='Place original PDF pages on the left and translated pages on the right, locally.')
    parser.add_argument('original', type=Path)
    parser.add_argument('translation', type=Path)
    parser.add_argument('-o', '--output', required=True, type=Path, help='New output PDF; existing files are not overwritten')
    parser.add_argument('--source-start', type=int, default=1, help='First original page number (default: 1)')
    parser.add_argument('--translation-start', type=int, default=1, help='First translated page number (default: 1)')
    parser.add_argument('--pages', type=int, help='Number of consecutive page pairs; required if remaining page counts differ')
    args = parser.parse_args(argv)
    try:
        count = build(args.original, args.translation, args.output, args.source_start, args.translation_start, args.pages)
    except ReviewError as exc:
        print(f'Could not create the review PDF: {exc}', file=sys.stderr)
        return 1
    except Exception:
        # Parser and filesystem exceptions may contain user data or paths.
        print('Could not create the review PDF. Check the inputs and output location.', file=sys.stderr)
        return 1
    print(f'Created {count} page pair(s). Original is left; translation is right. Review every pair manually.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
