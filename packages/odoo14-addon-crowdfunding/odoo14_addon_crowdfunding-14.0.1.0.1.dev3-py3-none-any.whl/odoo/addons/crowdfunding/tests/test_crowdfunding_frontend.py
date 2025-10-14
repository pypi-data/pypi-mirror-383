import odoo
import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class TestCrowdfundingFrontend(odoo.tests.HttpCase):
    def test_pledge_not_logged_in(self):
        """
        Test pledging for a challenge without being logged in
        """
        self.skipTest("Skip tour tests until weird CI issue is solved")
        challenge = self.env.ref("crowdfunding.demo_challenge")
        self.start_tour("/", "crowdfunding_frontend")
        self.assertEqual(challenge.pledged_amount_unpaid, 4242)
        self.assertEqual(
            challenge.invoice_ids.partner_id.name,
            "Firstname Lastname",
        )
