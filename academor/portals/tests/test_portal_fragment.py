from django.test import SimpleTestCase

from portals.utils.portal_fragment import build_fragment_document


class PortalFragmentTests(SimpleTestCase):
    def test_build_fragment_includes_nav_snapshot_for_active_states(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Scores</title></head>
        <body>
          <aside class="admin-sidebar" id="adminSidebar">
            <nav class="sidebar-nav">
              <a class="nav-link" href="/portal/parent/"><span class="nav-icon"></span></a>
              <a class="nav-link active" href="/portal/parent/scores/"><span class="nav-icon"></span></a>
            </nav>
          </aside>
          <nav class="mobile-bottom-nav d-lg-none">
            <a class="mobile-nav-item" href="/portal/parent/">Home</a>
            <a class="mobile-nav-item active" href="/portal/parent/scores/">Scores</a>
          </nav>
          <main class="dashboard-content" data-portal-content-root>
            <div class="container-fluid"><h1>Scores</h1></div>
          </main>
        </body>
        </html>
        """

        fragment = build_fragment_document(html)

        self.assertIn('id="portal-nav-snapshot"', fragment)
        self.assertIn('class="nav-link active"', fragment)
        self.assertIn('class="mobile-nav-item active"', fragment)
        self.assertIn('<h1>Scores</h1>', fragment)
        self.assertNotIn('<title>Scores</title>', fragment.split('</head>', 1)[1])

    def test_build_fragment_preserves_badge_snapshot(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        <body>
          <main class="dashboard-content" data-portal-content-root>
            <div class="container-fluid">
              <h1>Dashboard</h1>
              <div hidden id="portal-badge-snapshot" data-unread-notifications="2"></div>
            </div>
          </main>
        </body>
        </html>
        """

        fragment = build_fragment_document(html)

        self.assertIn('id="portal-badge-snapshot"', fragment)
        self.assertIn('data-unread-notifications="2"', fragment)
