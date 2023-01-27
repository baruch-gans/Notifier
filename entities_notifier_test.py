import unittest
from datetime import datetime

from brew_notifier_assignment.entities import Company
from brew_notifier_assignment.entities import Event, CRAWLING_STATUSES, CompanyForWebinar, Webinar
from brew_notifier_assignment.notifier_v2 import notify, EntityLogic


class TestBaseEntityLogic(unittest.TestCase):
    def test_check_if_notify(self):
        # Test for Event
        event = Event(is_deleted=False, crawling_status=CRAWLING_STATUSES.TEXT_ANALYZED,
                      link='https://www.example.com',
                      name='Example', start_date=datetime.now())
        original_event = Event(is_deleted=False, crawling_status=CRAWLING_STATUSES.NOT_CRAWLED,
                               link='https://www.example.com/event',
                               name='Example', start_date=datetime.now())
        entity_logic = EntityLogic(entity_obj=event, original_entity_obj=original_event, entity_type="Event")
        self.assertTrue(entity_logic.check_if_notify())

        # Test for Company
        company = Company(employees_min=2, employees_max=10, link='https://www.example.com', name='Example',
                          is_blacklisted=True)

        original_company = Company(employees_min=30, employees_max=40, link='https://www.example2.com', name='Example2',
                                   is_blacklisted=False)

        entity_logic = EntityLogic(entity_obj=company, original_entity_obj=original_company, entity_type="Company")
        self.assertFalse(entity_logic.check_if_notify())

        # Test for original_entity_obj is None
        entity_logic = EntityLogic(entity_obj=company, original_entity_obj=None, entity_type="Company")
        self.assertTrue(entity_logic.check_if_notify())

        # Test for current_entity_obj is None
        entity_logic = EntityLogic(entity_obj=None, original_entity_obj=original_company, entity_type="Company")
        self.assertTrue(entity_logic.check_if_notify())

    def test_check_notify_on(self):
        # Test for Event
        event = Event(is_deleted=False, crawling_status=CRAWLING_STATUSES.TEXT_ANALYZED,
                      link='https://www.example.com/event',
                      name='Example', start_date=datetime.now())
        original_event = Event(is_deleted=False, crawling_status=CRAWLING_STATUSES.NOT_CRAWLED,
                               link='https://www.example.com/event',
                               name='Example', start_date=datetime.now())
        entity_logic = EntityLogic(entity_obj=event, original_entity_obj=original_event, entity_type="Event")
        self.assertEqual(event, entity_logic.notify_on())
        self.assertEqual(notify(event, original_event, "Event"), event)

        # Test CompanyForWebinar
        webinar = Webinar(link="https://example.com/webinar", name="Example Webinar", start_date=datetime.now())
        company = Company(link="https://example.com/company", name="Example Company", employees_min=10,
                          employees_max=100)

        original_company_for_webinar = CompanyForWebinar(webinar=webinar, company=company)
        company_for_webinar = CompanyForWebinar(webinar=webinar, company=company, is_blacklisted=True)
        entity_logic = EntityLogic(entity_obj=company_for_webinar, original_entity_obj=original_company_for_webinar,
                                   entity_type="CompanyForWebinar")
        self.assertEqual(company_for_webinar.webinar, entity_logic.notify_on())
        self.assertEqual(notify(company_for_webinar, original_company_for_webinar, "CompanyForWebinar"),
                         company_for_webinar.webinar)
