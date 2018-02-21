# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestSaleMarketing(common.TransactionCase):

    def setUp(self):
        super(TestSaleMarketing, self).setUp()
        cr, uid = self.cr, self.uid
        self.sale_order_model = self.env['sale.order']
        self.crm_lead_model = self.env['crm.lead']
        self.crm_campaign_model = self.env['crm.tracking.campaign']
        self.crm_medium_model = self.env['crm.tracking.medium']
        self.crm_source_model = self.env['crm.tracking.source']
        self.crm_sale_model = self.env['crm.make.sale']
        self.res_users = self.env['res.users']

        # company
        self.company1 = self.env.ref('base.main_company')
        # users
        self.admin_user = self.env.ref('base.user_root')
        self.sale_user = self._create_user(
            'sale_user', [self.env.ref('base.group_sale_salesman')],
            self.company1)

        # Create CRM Leads
        self.campaign = self._create_campaign()
        self.medium = self._create_medium()
        self.source = self._create_source()
        self.lead = self._create_crm_lead(self.campaign, self.medium,
                                          self.source)
        self.sale = self._create_quotation(cr, uid)

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.res_users.with_context({'no_reset_password': True}).create({
                'name': 'Test User',
                'login': login,
                'password': 'demo',
                'email': 'test@yourcompany.com',
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, group_ids)]
            })
        return user

    def _create_campaign(self):
        """Create a Campaign."""
        campaign = self.crm_campaign_model.sudo(self.admin_user).create({
            'name': 'Christmas Campaign',
        })
        return campaign

    def _create_medium(self):
        """Create a Medium."""
        medium = self.crm_medium_model.sudo(self.admin_user).create({
            'name': 'Email',
            'active': True
        })
        return medium

    def _create_source(self):
        """Create a Source."""
        source = self.crm_source_model.sudo(self.admin_user).create({
            'name': 'Mail',
        })
        return source

    def _create_crm_lead(self, campaign, medium, source):
        """Create a Lead."""
        crm = self.crm_lead_model.sudo(self.sale_user).create({
            'name': 'CRM LEAD',
            'type': 'opportunity',
            'active': True,
            'partner_id': self.sale_user.id,
            'campaign_id': campaign.id,
            'medium_id': medium.id,
            'source_id': source.id,
        })
        return crm

    def _create_quotation(self, cr, uid):
        """Convert a Opportunity to Quotation."""
        crm_make_sale = self.crm_sale_model.sudo(self.sale_user).create({
            'close': True,
            'partner_id': self.lead.partner_id.id,
        })
        context = {'active_id': self.lead.id,
                   'active_ids': self.lead.ids,
                   'active_model': 'crm.lead',
                   'stage_type': 'opportunity',
                   }
        res = self.registry('crm.make.sale').makeOrder(cr, uid,
                                                       crm_make_sale.ids,
                                                       context)
        sale_id = res.get('res_id')
        sale = self.sale_order_model.browse(sale_id)
        return sale

    def test_marketing_details(self):
        self.assertEqual(self.lead.campaign_id,
                         self.sale.campaign_id,
                         'Campaign for sale and lead does not match')
        self.assertEqual(self.lead.medium_id,
                         self.sale.medium_id,
                         'Medium for sale and lead does not match')
        self.assertEqual(self.lead.source_id,
                         self.sale.source_id,
                         'Source for sale and lead does not match')
