"""
English help copy shown at the top of every Django admin list and edit page.
Written for non-technical staff — explains what each section is and what it affects on the site.
"""

ADMIN_HELP = {
  # --- Media & landing content ---
  'Media': {
    'title': 'Page background images',
    'summary': (
      'Upload hero/banner images for individual site pages. Each image can be assigned to '
      'one page header (About, Contact, Courses, Tests, Services, Study abroad).'
    ),
    'where': 'Shown as the large background at the top of the matching public page.',
    'tips': [
      'Tick only ONE page per image when possible.',
      'Study abroad uses its own image; if none is set, the About page image is used as fallback.',
      'Images assigned to a page header are not auto-compressed — use good quality originals.',
    ],
  },
  'About': {
    'title': 'About us content',
    'summary': (
      'Main "About Academor" text, homepage visibility, photo gallery, and intro video.'
    ),
    'where': (
      'Homepage About block (if "Show on homepage" is on), full About page (/about/), '
      'and the gallery under the About image.'
    ),
    'tips': [
      'Gallery: add up to 12 images in the Media section below — each can have name/role/tag in AZ, EN, RU.',
      'Video: upload a cover image (poster) and a video file; cover shows until the visitor presses play.',
      '"Show on homepage" hides or shows the About section on the main page only.',
    ],
  },
  'AboutWhyItem': {
    'title': 'Why Academor? highlights',
    'summary': 'Short icon + title + text blocks shown under the About page image.',
    'where': 'About page, in the "Why Academor?" section below the main image.',
    'tips': [
      'Icon = Font Awesome 5 class, e.g. fa-graduation-cap (see fontawesome.com/icons).',
      'Lower "Order" number = appears first. Turn off "Active" to hide without deleting.',
    ],
  },
  'SiteFaqEntry': {
    'title': 'FAQ (frequently asked questions)',
    'summary': 'Question and answer pairs for the accordion on the About page.',
    'where': 'About page FAQ section.',
    'tips': [
      'Lower order number = appears higher in the list.',
      'Fill AZ, EN, and RU for all three site languages.',
      'Duplicate order numbers are shifted automatically when you save.',
    ],
  },
  'Contact': {
    'title': 'Contact information',
    'summary': (
      'Office address, phone numbers, emails, social media links, and Google Maps embed.'
    ),
    'where': 'Site footer on every page and the Contact page (/contact/).',
    'tips': [
      'Map: in Google Maps use Share -> Embed map -> copy only the iframe src URL.',
      'WhatsApp numbers appear as clickable chat links.',
      'Usually only ONE Contact record exists — edit it, do not create duplicates.',
    ],
  },

  # --- Team, reviews, blog ---
  'Team': {
    'title': 'Team members & trainers',
    'summary': 'Staff profiles: photo, name, role, bio, and social links.',
    'where': 'Team page (/team/) and trainer lists on course pages.',
    'tips': [
      'Slug is auto-generated from the name — used in URLs.',
      'Lower "Order" = appears earlier on the Team page.',
      'Assign trainers to courses in the Service (course) edit page.',
    ],
  },
  'Review': {
    'title': 'Customer reviews / testimonials',
    'summary': 'Visitor-submitted or manually added reviews with star rating.',
    'where': 'Reviews section on the site (when "Active" is checked).',
    'tips': [
      'Uncheck "Active" to hide a review without deleting it.',
      'Rating is 1–5 stars.',
    ],
  },
  'BlogPost': {
    'title': 'Blog / news articles',
    'summary': 'News posts with title, body, date, cover/video, tags, and up to 6 gallery images.',
    'where': 'Blog list (/blog/) and article detail pages. "On main page" shows on homepage.',
    'tips': [
      '"On top" pins the post to the top of the blog list.',
      '"On main page" shows a card on the homepage.',
      'Tags: pick from Tags section (create tags first under Tags in admin).',
      'Cover image is used for list thumbnails and as the video poster.',
      'If a video is uploaded, it is shown large at the top of the article.',
      'Without a cover, the first gallery image is used as the thumbnail.',
      'Slug is auto-generated — do not change unless you know SEO implications.',
    ],
  },
  'ContentTag': {
    'title': 'Tags (blog)',
    'summary': (
      'Topic labels such as IELTS or Speaking for blog articles. '
      'Shown on the blog list, article pages, and /blog/tag/… filters.'
    ),
    'where': 'Public blog pages only (not services/course cards on the site).',
    'tips': [
      'Create tags here first, then assign them on Blog posts.',
      'Services can also use tags in admin for SEO keywords only (not shown on site).',
      'Azerbaijani name is required; EN/RU names are optional.',
      'Lower order number = listed first in tag filters.',
      'Turn off Active to hide a tag without deleting it.',
    ],
  },

  # --- Courses & pricing ---
  'Service': {
    'title': 'Courses / services (programs)',
    'summary': (
      'Each row is one Academor program: General English, IELTS, GMAT, study abroad prep, etc. '
      'Includes descriptions, trainers, price packages, and card icon.'
    ),
    'where': (
      'Courses list (/courses/), course detail pages, homepage service cards, '
      'and the payment modal when a visitor buys a package.'
    ),
    'tips': [
      'Add price packages in the table below (months, lessons, price in AZN).',
      'Upload ONE thumbnail image in the Media inline at the bottom.',
      'Card icon: shown on homepage and courses list; "Default" auto-detects from the URL slug.',
      'Tags: optional — used for SEO keywords on course pages (not shown to visitors).',
      '"Show on main page" controls homepage visibility. '
      'Order: 0 = first, 1 = next (site, admin list, and Courses dropdown).',
      'Slug is hidden — it is set automatically from the Azerbaijani name.',
    ],
  },

  'Tagline': {
    'title': 'Page banner taglines',
    'summary': (
      'Short Azerbaijani text shown on each inner page hero banner (animated). '
      'One row per page — homepage is not included.'
    ),
    'where': (
      'Top banner on About, Contact, Courses, Services, Tests, Study abroad, Blog, Team, '
      'and detail pages that share those banners.'
    ),
    'tips': [
      'Pick the page — only one tagline row per page.',
      'Description (AZ) is the only field; keep it to one or two short lines.',
      'Turn off Active to hide without deleting.',
    ],
  },
  'CoursePricePackage': {
    'title': 'Course price packages',
    'summary': (
      'Pricing tiers for a course: tab category, name, months, lesson count, '
      'lesson length, and price.'
    ),
    'where': (
      'Course detail page payment tabs, the payment popup, and the homepage '
      '"Most in demand" price carousel (when "Show on homepage" is on).'
    ),
    'tips': [
      'Payment tab: group/individual, standard/intensive, full package (group/individual), or installments.',
      'Link each package to the correct course.',
      'Lower "Order" = appears first within the same tab on the course page.',
      '"Premium" marks a highlighted/recommended package in the UI.',
      '"Show on homepage" adds the package to the homepage price carousel (any course).',
      'Turn off "Active" to hide a package without deleting it.',
    ],
  },
  'Sale': {
    'title': 'Promotions & discounts',
    'summary': (
      'Sales campaigns: percentage discounts, end date, optional banner image, '
      'and which courses are affected.'
    ),
    'where': 'Homepage promotion banner and discounted prices on selected courses.',
    'tips': [
      'Leave "Discount (%)" empty for announcement-only promos (no price change).',
      '"Apply discount to service prices" reduces listed prices — requires a % and selected courses.',
      'Leave services empty for a general homepage announcement without price changes.',
      'Upload one card image in the Media section below for the promo banner.',
    ],
  },

  # --- Study abroad ---
  'AbroadModel': {
    'title': 'Study abroad programs',
    'summary': (
      'Country/program cards for study abroad: image, name, description, detail page content.'
    ),
    'where': 'Study abroad page (/abroad/), homepage abroad section, and program detail pages.',
    'tips': [
      '"Show on main page" controls homepage visibility.',
      'Slug is used in URLs — e.g. /abroad/germany/.',
      'Detail page image is shown on the individual program page header.',
    ],
  },
  'StudyAbroadSection': {
    'title': 'Study abroad intro text',
    'summary': 'Single block of introductory text for the study abroad section.',
    'where': 'Top of /abroad/ page and related homepage section.',
    'tips': [
      'Only ONE record is allowed — edit the existing one, do not add another.',
      'Fill text in AZ, EN, and RU.',
    ],
  },
  'StudyAbroadAdvantage': {
    'title': 'Study abroad advantage highlights',
    'summary': 'Small icon + label items shown under the study abroad hero (e.g. "Free consultation").',
    'where': 'Homepage study abroad block and /abroad/ page hero area.',
    'tips': [
      'Icon = Font Awesome 5 class, e.g. fa-certificate.',
      'Must be linked to the Study Abroad Section record.',
      'Lower order = appears first.',
    ],
  },
  'University': {
    'title': 'Partner universities',
    'summary': 'Universities listed under a study abroad program: name, flag, website, description.',
    'where': 'Inside each study abroad program detail page, in the universities list.',
    'tips': [
      'Select which study abroad program this university belongs to.',
      'Slug is auto-generated from the name.',
      'Turn off "Active" to hide without deleting.',
    ],
  },

  # --- Inbound messages ---
  'ContactInquiry': {
    'title': 'Contact form messages',
    'summary': 'Messages submitted by visitors through the site contact form.',
    'where': 'This admin only — visitors do not see this list.',
    'tips': [
      'Check "Read" when you have handled a message — unread items show a red badge.',
      'Click the sender name to open the full message.',
      'All fields are read-only except the "Read" checkbox.',
    ],
  },

  # --- Tests ---
  'Test': {
    'title': 'Online tests',
    'summary': 'Placement or language tests: title, description, active flag.',
    'where': 'Tests list page (/tests/) and individual test pages.',
    'tips': [
      'Add questions in the Questions section (separate admin page).',
      'Turn off "Active" to hide a test from the public site.',
    ],
  },
  'Question': {
    'title': 'Test questions',
    'summary': 'Individual questions belonging to a test, with up to 5 answer options.',
    'where': 'Shown during the test on the public site.',
    'tips': [
      'Mark exactly one option as correct (or multiple if your test logic allows).',
      'Maximum 5 options per question.',
      '"Order" controls question sequence within the test.',
    ],
  },
  'UserResult': {
    'title': 'Test submissions (results)',
    'summary': 'Records of visitors who completed a test: name, contact, score, level.',
    'where': 'This admin only — for your review and follow-up.',
    'tips': [
      'Read-only — results are created automatically when someone finishes a test.',
      'Use filters to find results by test or date.',
    ],
  },

  # --- Payments (payments app) ---
  'Payment': {
    'title': 'Payment transactions',
    'summary': (
      'All card payments processed through the Epoint gateway when visitors buy a course package.'
    ),
    'where': 'This admin only — linked to Course enrollments below.',
    'tips': [
      'Read-only — records are created automatically by the payment system.',
      'Status: pending, completed, failed, etc.',
      'Use search to find by transaction ID, email, or contract number.',
    ],
  },
  'CourseEnrollment': {
    'title': 'Course enrollments & contracts',
    'summary': (
      'After a successful payment, an enrollment record is created with the signed training agreement.'
    ),
    'where': 'This admin only — download the PDF contract for your records.',
    'tips': [
      'Read-only — created automatically after payment.',
      'Click "Download PDF" to save the training agreement.',
      'Contract number is unique per enrollment.',
    ],
  },
}

ADMIN_INDEX_HELP = {
  'title': 'Academor site administration',
  'summary': (
    'Everything you change here appears on the public website (academor.az). '
    'Each section below manages a specific part of the site. Open any item to see a detailed '
    'explanation at the top of the page.'
  ),
  'sections': [
    {
      'name': 'Content & landing',
      'items': 'Media, About, FAQ, Contact',
      'desc': 'Page backgrounds, about text, FAQ, and contact details in the footer.',
    },
    {
      'name': 'Team & marketing',
      'items': 'Team, Reviews, Blog, Tags',
      'desc': 'Staff profiles, testimonials, news articles, and topic tags for blog/services.',
    },
    {
      'name': 'Courses & sales',
      'items': 'Services, Price packages, Sales',
      'desc': 'Course programs, pricing tiers, and promotional discounts.',
    },
    {
      'name': 'Study abroad',
      'items': 'Abroad programs, Section text, Advantages, Universities',
      'desc': 'Study abroad cards, intro text, highlights, and partner universities.',
    },
    {
      'name': 'Messages & tests',
      'items': 'Contact inquiries, Tests, Questions, Results',
      'desc': 'Form submissions and online placement tests.',
    },
    {
      'name': 'Payments',
      'items': 'Payments, Course enrollments',
      'desc': 'Card transactions and signed training agreements (read-only).',
    },
  ],
}


def get_admin_help(model):
  """Return help dict for a model class, or None."""
  name = model.__name__
  return ADMIN_HELP.get(name)
