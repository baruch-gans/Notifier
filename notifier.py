from abc import abstractmethod
from typing import Type, Union

from brew_notifier_assignment.entities import (CRAWLING_STATUSES, ENTITY_TYPES,
                                               Event, Company, Webinar, ContentItem,
                                               CompanyForEvent, CompanyForWebinar,
                                               CompanyCompetitor)

EntityType = Union[Event, Company, Webinar, ContentItem, CompanyForEvent, CompanyForWebinar, CompanyCompetitor]

EXTERNAL_API_URL = "www.example.com"


class BaseEntityLogic:
    def __init__(self, entity_obj: EntityType, original_entity_obj: EntityType) -> None:
        self.entity_obj = entity_obj
        self.original_entity_obj = original_entity_obj

    @abstractmethod
    def check_if_notify(self) -> bool:
        raise NotImplementedError("Subclass must implement this method")

    @abstractmethod
    def notify_on(self) -> EntityType:
        raise NotImplementedError("Subclass must implement this method")

    def notify(self):
        entity_to_notify_on = self.notify_on()
        print("Notifying on:", entity_to_notify_on.__dict__)
        print("Original: ", self.original_entity_obj.__dict__)
        print("Current: ", self.entity_obj.__dict__)
        return entity_to_notify_on
        # TODO: On real API:
        # requests.post(EXTERNAL_API_URL, json=entity_to_notify_on)

    def has_base_changed(self) -> bool:
        return self.original_entity_obj is None \
               or self.entity_obj is None \
               or self.original_entity_obj.is_deleted != self.entity_obj.is_deleted

    def has_crawling_status_changed_to_analyzed_or_uploaded(self) -> bool:
        return self.original_entity_obj.crawling_status != self.entity_obj.crawling_status \
               and self.entity_obj.crawling_status in [CRAWLING_STATUSES.TEXT_ANALYZED, CRAWLING_STATUSES.TEXT_UPLOADED]

    def has_blacklist_status_changed(self) -> bool:
        return self.original_entity_obj.is_blacklisted != self.entity_obj.is_blacklisted


class EventNotifierLogic(BaseEntityLogic):

    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_blacklist_status_changed,
                  self.has_crawling_status_changed_to_analyzed_or_uploaded]
        return all(check() for check in checks)

    def notify_on(self) -> EntityType:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj


class CompanyLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_crawling_status_changed_to_analyzed_or_uploaded]
        return all(check() for check in checks)

    def notify_on(self) -> EntityType:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj


class WebinarLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_blacklist_status_changed,
                  self.has_crawling_status_changed_to_analyzed_or_uploaded]
        return all(check() for check in checks)

    def notify_on(self) -> EntityType:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj


class ContentItemLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_blacklist_status_changed,
                  self.has_crawling_status_changed_to_analyzed_or_uploaded]
        return all(check() for check in checks)

    def notify_on(self) -> Company:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj.company


class CompanyForEventLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_blacklist_status_changed]
        return all(check() for check in checks)

    def notify_on(self) -> Event:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj.event


class CompanyForWebinarLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed, self.has_blacklist_status_changed]
        return all(check() for check in checks)

    def notify_on(self) -> Webinar:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj.webinar


class CompanyCompetitorLogic(BaseEntityLogic):
    def check_if_notify(self) -> bool:
        checks = [self.has_base_changed]
        return all(check() for check in checks)

    def notify_on(self) -> Company:
        entity_obj = self.entity_obj or self.original_entity_obj
        return entity_obj.company


def notify(entity_obj: EntityType, original_entity_obj: EntityType, entity_type: str):
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"{entity_type} not supported, supported entities are: {ENTITY_TYPES}")

    entity_logic_mapper = {
        "Event": EventNotifierLogic,
        "Company": CompanyLogic,
        "Webinar": WebinarLogic,
        "ContentItem": ContentItemLogic,
        "CompanyForEvent": CompanyForEventLogic,
        "CompanyForWebinar": CompanyForWebinarLogic,
        "CompanyCompetitor": CompanyCompetitorLogic
    }

    entity_logic = entity_logic_mapper[entity_type](entity_obj=entity_obj, original_entity_obj=original_entity_obj)
    if entity_logic.check_if_notify():
        entity_logic.notify()
