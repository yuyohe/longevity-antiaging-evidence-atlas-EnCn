import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_visual_feishu_assets_2026_05 import load_font, text_len, wrap_text


class VisualTextTests(unittest.TestCase):
    def test_closing_punctuation_does_not_start_a_line(self):
        draw = ImageDraw.Draw(Image.new("RGB", (400, 200)))
        font = load_font(31)
        text = "检测和补充策略宜结合医生建议。"
        width = text_len(draw, text[:-1], font)
        lines = wrap_text(draw, text, font, width)
        self.assertEqual("".join(lines), text)
        self.assertTrue(all(not line.startswith("。") for line in lines))
        self.assertTrue(all(text_len(draw, line, font) <= width for line in lines))


if __name__ == "__main__":
    unittest.main()
