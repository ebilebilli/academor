from django.test import SimpleTestCase

from projects.templatetags.rich_text import tidy_rich_text


class TidyRichTextTests(SimpleTestCase):
    def test_pasted_word_noise_is_removed_and_content_kept(self):
        html = (
            '<p style="text-align:justify; line-height:2.5; margin-bottom:24px">'
            '<span style="font-size:18pt; color:#ff5414"><strong>IELTS</strong></span>&nbsp;&nbsp;kursu</p>'
            '<p>&nbsp;</p><p><br></p><p><span>&nbsp;</span></p>'
            '<p>Birinci<br><br><br>ikinci<br></p><div>&nbsp;</div>'
            '<ul><li><br>bir</li></ul><h3 style="font-family:Calibri">Başlıq</h3>'
        )
        self.assertEqual(
            tidy_rich_text(html),
            '<p><span style="color:#ff5414"><strong>IELTS</strong></span> kursu</p>'
            '<p>Birinci<br>ikinci</p><ul><li>bir</li></ul><h3>Başlıq</h3>',
        )

    def test_clean_text_is_unchanged(self):
        html = '<h2>Kurs</h2><p>Mətn <a href="/x">link</a>.</p><ol><li>Bir</li></ol>'
        self.assertEqual(tidy_rich_text(html), html)

    def test_empty(self):
        self.assertEqual(tidy_rich_text(None), '')
