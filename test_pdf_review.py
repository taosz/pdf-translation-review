import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz  # Only needed for these local tests, not by the tool.
from pypdf import PdfReader, PdfWriter
from pdf_review import ReviewError, build


def sample(path, label, pages, rotate=False):
    doc = fitz.open()
    for number in range(1, pages + 1):
        page = doc.new_page(width=400, height=600)
        page.insert_text((40, 100), f'{label}{number}')
        if rotate:
            page.set_rotation(90)
    doc.save(path)
    doc.close()


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source, self.translated, self.output = (self.root / n for n in ('a.pdf', 'b.pdf', 'out.pdf'))
        sample(self.source, 'SOURCE', 3)
        sample(self.translated, 'TRANSLATED', 2, rotate=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_selected_pages_are_placed_on_expected_sides(self):
        self.assertEqual(build(self.source, self.translated, self.output, 2, 1, 2), 2)
        doc = fitz.open(self.output)
        self.assertEqual(len(doc), 2)
        for page, left, right in [(doc[0], 'SOURCE2', 'TRANSLATED1'), (doc[1], 'SOURCE3', 'TRANSLATED2')]:
            words = {w[4]: w[0] for w in page.get_text('words')}
            self.assertLess(words[left], 612)
            self.assertGreater(words[right], 612)
        doc.close()

    def test_mismatch_out_of_range_and_overwrite_are_rejected(self):
        with self.assertRaisesRegex(ReviewError, 'counts differ'):
            build(self.source, self.translated, self.output)
        with self.assertRaisesRegex(ReviewError, 'outside'):
            build(self.source, self.translated, self.output, 3, 1, 2)
        self.assertFalse(self.output.exists())
        self.output.write_bytes(b'keep this file')
        with self.assertRaisesRegex(ReviewError, 'already exists'):
            build(self.source, self.translated, self.output, 2, 1, 2)
        self.assertEqual(self.output.read_bytes(), b'keep this file')
        with self.assertRaisesRegex(ReviewError, 'already exists'):
            build(self.source, self.translated, self.source, 2, 1, 2)

    def test_encrypted_pdf_is_rejected_without_output(self):
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.encrypt('password')
        with self.translated.open('wb') as file:
            writer.write(file)
        with self.assertRaisesRegex(ReviewError, 'Encrypted'):
            build(self.source, self.translated, self.output, 1, 1, 1)
        self.assertFalse(self.output.exists())

    def test_source_and_translation_are_unchanged(self):
        first, second = self.source.read_bytes(), self.translated.read_bytes()
        build(self.source, self.translated, self.output, 2, 1, 2)
        self.assertEqual(self.source.read_bytes(), first)
        self.assertEqual(self.translated.read_bytes(), second)
        self.assertEqual(len(PdfReader(self.output).pages), 2)

    def test_assembly_does_not_open_a_network_socket(self):
        with patch('socket.socket', side_effect=AssertionError('network used')):
            self.assertEqual(build(self.source, self.translated, self.output, 2, 1, 2), 2)


if __name__ == '__main__':
    unittest.main()
