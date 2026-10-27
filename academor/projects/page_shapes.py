"""Decorative shapes — a different set per public page, in three layers.

  banner  bold shapes in the corners of the dark page-header band (inner pages)
          (shape, colour, size px, corner tl|tr|bl|br, rotation deg, motion)
  back    large soft shapes behind the content; cards paint over them, they show in the
          gaps between sections (shape, colour, size px, left %, top %, rotation, motion)
  edge    small bold shapes peeking in from the page edge, in front of the content but
          never past the gutter (shape, colour, size px, side l|r, top %, rotation, motion)

shape   symbol id in assets/img/shapes/shapes.svg (Adobe Stock vectors, see shapes.css)
colour  orange | teal | indigo | peach | lilac | sky | blush — brand palette tints
motion  'spin' (very slow turn), 'float' (gentle bob) or '' (still)
The homepage keeps its right gutter for the flight route, so its edge shapes sit left.
"""

_DEFAULT = {
    'banner': [('sparkle', 'orange', 120, 'bl', 0, 'spin'), ('cloud', 'indigo', 200, 'tr', 0, 'float')],
    'back': [('blob-flower', 'lilac', 420, 14, 18, 0, 'float'), ('cushion', 'sky', 380, 86, 55, 20, '')],
    'edge': [('asterisk', 'orange', 90, 'r', 30, 0, 'spin')],
}

PAGE_SHAPES = {
    'home-page': {
        'banner': [],
        'back': [
            ('cloud', 'lilac', 520, 14, 16, 0, 'float'),
            ('wave', 'sky', 420, 86, 33, -8, ''),
            ('blob-flower', 'blush', 460, 14, 52, 24, 'float'),
            ('cushion', 'lilac', 420, 86, 70, 0, ''),
            ('drop', 'sky', 380, 14, 86, -30, 'float'),
        ],
        'edge': [
            ('burst', 'orange', 110, 'l', 12, 0, 'spin'),
            ('sparkle', 'indigo', 90, 'l', 44, 15, 'spin'),
            ('star', 'teal', 90, 'l', 78, 10, 'spin'),
        ],
    },
    'about-page': {
        'banner': [('daisy', 'orange', 170, 'bl', 0, 'spin'), ('arch', 'indigo', 210, 'tr', 180, '')],
        'back': [('arch', 'sky', 460, 14, 30, 0, ''), ('blob-flower', 'blush', 420, 86, 62, 30, 'float')],
        'edge': [('sparkle', 'indigo', 90, 'r', 22, 0, 'spin'), ('star', 'orange', 80, 'l', 74, 0, 'spin')],
    },
    'services-page': {
        'banner': [('cog', 'indigo', 160, 'br', 0, 'spin'), ('quarter', 'orange', 170, 'tl', 0, '')],
        'back': [('cushion', 'lilac', 440, 86, 28, 15, 'float'), ('quarter', 'blush', 400, 14, 64, 90, '')],
        'edge': [('asterisk', 'orange', 90, 'l', 30, 0, 'spin'), ('badge', 'indigo', 90, 'r', 78, 0, 'spin')],
    },
    'courses-page': {
        'banner': [('pinwheel', 'orange', 160, 'bl', 0, 'spin'), ('stack', 'indigo', 170, 'tr', 0, '')],
        'back': [('drop', 'sky', 420, 86, 30, -20, 'float'), ('stack', 'blush', 380, 14, 66, 0, '')],
        'edge': [('spark-lines', 'teal', 90, 'l', 24, 0, 'spin'), ('pinwheel', 'indigo', 90, 'r', 70, 0, 'spin')],
    },
    'abroad-page': {
        'banner': [('sun', 'orange', 180, 'br', 0, 'spin'), ('cloud', 'indigo', 210, 'tl', 0, 'float')],
        'back': [('cloud', 'sky', 480, 14, 22, 0, 'float'), ('wave', 'blush', 420, 86, 52, 8, ''), ('star-soft', 'lilac', 360, 14, 82, 12, 'spin')],
        'edge': [('star-soft', 'indigo', 90, 'r', 18, 12, 'spin'), ('sparkle', 'orange', 80, 'l', 60, 0, 'spin')],
    },
    'team-page': {
        'banner': [('ring-flower', 'orange', 170, 'bl', 0, 'spin'), ('tomb', 'indigo', 170, 'tr', 0, '')],
        'back': [('tomb', 'lilac', 440, 86, 24, 0, ''), ('clover', 'blush', 400, 14, 56, 25, 'float'), ('cloud', 'sky', 420, 86, 84, 0, 'float')],
        'edge': [('sparkle', 'teal', 90, 'l', 30, 0, 'spin'), ('ring-flower', 'orange', 90, 'r', 64, 0, 'spin')],
    },
    'blog-page': {
        'banner': [('swirl', 'orange', 170, 'br', 0, 'spin'), ('cushion', 'indigo', 180, 'tl', 0, 'float')],
        'back': [('cushion', 'blush', 440, 14, 30, 0, 'float'), ('badge', 'sky', 400, 86, 66, 0, 'spin')],
        'edge': [('cross', 'orange', 90, 'r', 26, 20, ''), ('swirl', 'indigo', 90, 'l', 74, 0, 'spin')],
    },
    'contact-page': {
        'banner': [('petals', 'orange', 170, 'bl', 0, 'spin'), ('arch', 'indigo', 200, 'tr', 180, '')],
        'back': [('arch', 'lilac', 440, 86, 40, 180, ''), ('petals', 'blush', 380, 14, 70, 0, 'spin')],
        'edge': [('star', 'indigo', 80, 'l', 30, -10, 'spin')],
    },
    'mock-tests-page': {
        'banner': [('plus-gear', 'orange', 160, 'br', 0, 'spin'), ('drop', 'indigo', 170, 'tl', 40, 'float')],
        'back': [('drop', 'blush', 420, 86, 26, 40, 'float'), ('quatrefoil', 'sky', 400, 14, 62, 0, '')],
        'edge': [('sparkle', 'orange', 80, 'l', 34, 0, 'spin'), ('plus-gear', 'indigo', 80, 'r', 76, 0, 'spin')],
    },
    'tests-page': {
        'banner': [('molecule', 'orange', 160, 'bl', 0, 'spin'), ('blob-flower', 'indigo', 190, 'tr', 0, 'float')],
        'back': [('blob-flower', 'lilac', 440, 14, 34, 0, 'float'), ('molecule', 'sky', 360, 86, 70, 0, 'spin')],
        'edge': [('asterisk', 'indigo', 80, 'r', 26, 0, 'spin')],
    },
    'results-page': {
        'banner': [('burst', 'orange', 170, 'br', 0, 'spin'), ('stack', 'indigo', 170, 'tl', 0, '')],
        'back': [('stack', 'lilac', 420, 14, 38, 0, ''), ('burst', 'blush', 380, 86, 72, 0, 'spin')],
        'edge': [('star', 'teal', 80, 'r', 30, 0, 'spin')],
    },
    'english-conversation-topics': {
        'banner': [('bloom', 'orange', 170, 'bl', 0, 'spin'), ('cloud', 'indigo', 200, 'tr', 0, 'float')],
        'back': [('cloud', 'blush', 460, 86, 34, 0, 'float'), ('bloom', 'sky', 380, 14, 70, 0, 'spin')],
        'edge': [('spark-lines', 'orange', 80, 'l', 30, 0, 'spin')],
    },
    'lucky-wheel-page': {
        'banner': [('sun', 'orange', 170, 'bl', 0, 'spin'), ('star-soft', 'indigo', 150, 'tr', 0, 'spin')],
        'back': [('sun', 'blush', 420, 86, 40, 0, 'spin')],
        'edge': [],
    },
}

# detail pages share their section's set
for _detail, _parent in (
    ('course-detail', 'courses-page'),
    ('mock-test-detail', 'mock-tests-page'),
    ('abroad-detail', 'abroad-page'),
    ('abroad-university-detail', 'abroad-page'),
    ('team-detail', 'team-page'),
    ('blog-detail', 'blog-page'),
    ('blog-tag-page', 'blog-page'),
    ('test-take', 'tests-page'),
    ('english-conversation-topic-detail', 'english-conversation-topics'),
):
    PAGE_SHAPES[_detail] = PAGE_SHAPES[_parent]


def shapes_for(url_name):
    return PAGE_SHAPES.get(url_name or '', _DEFAULT)
