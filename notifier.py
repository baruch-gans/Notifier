from typing import Union

from brew_notifier_assignment.entities import (CRAWLING_STATUSES, ENTITY_TYPES,
                                               Event, Company, Webinar, ContentItem,
                                               CompanyForEvent, CompanyForWebinar,
                                               CompanyCompetitor)

EntityType = Union[Event, Company, Webinar, ContentItem, CompanyForEvent, CompanyForWebinar, CompanyCompetitor, None]

EXTERNAL_API_URL = "www.example.com"


class EntityLogic:
    def __init__(self, entity_obj: EntityType, original_entity_obj: EntityType, entity_type: str) -> None:
        """
        Initialize the class with the current and original entity objects and the entity type.
        :param entity_obj: The current entity object
        :param original_entity_obj: The original entity object
        :param entity_type: The type of the entity
        """
        self.entity_obj = entity_obj
        self.original_entity_obj = original_entity_obj
        self.entity_type = entity_type

    def check_if_notify(self) -> bool:
        """
        Check if the current and original entity objects are different and notify is needed.
        :return: True if notify is needed, False otherwise
        """
        checks = self.entity_checks_mapper[self.entity_type]
        return any(check(self) for check in checks)

    def notify_on(self) -> EntityType:
        """
        Get the object that should be notified on.
        :return: The object to notify on
        """
        notify_on_lambda = self.entity_notify_on_mapper[self.entity_type]
        notify_on_obj = notify_on_lambda(self.entity_obj or self.original_entity_obj)
        return notify_on_obj

    def common_changes_to_notify(self) -> bool:
        """
        Check if the common changes that need to be notified on have occurred.
        :return: True if changes have occurred, False otherwise
        """
        return self.original_entity_obj is None or self.entity_obj is None \
               or self.original_entity_obj.is_deleted != self.entity_obj.is_deleted

    def has_crawling_status_changed_to_analyzed_or_uploaded(self) -> bool:
        """
        Check if the crawling status has changed to "analyzed" or "uploaded"
        :return: True if the status has changed, False otherwise
        """
        return self.original_entity_obj.crawling_status != self.entity_obj.crawling_status \
               and self.entity_obj.crawling_status in [CRAWLING_STATUSES.TEXT_ANALYZED, CRAWLING_STATUSES.TEXT_UPLOADED]

    def has_blacklist_status_changed(self) -> bool:
        """
        Check if the blacklist status has changed
        :return: True if the status has changed, False otherwise
        """
        return self.original_entity_obj.is_blacklisted != self.entity_obj.is_blacklisted

    # This dictionary maps the entity_type to a list of check functions.
    # These functions are used to check if any changes have occurred on the
    # entity that require a notification to be sent.
    entity_checks_mapper = {
        "Event":
            [common_changes_to_notify, has_blacklist_status_changed,
             has_crawling_status_changed_to_analyzed_or_uploaded],
        "Company":
            [common_changes_to_notify, has_crawling_status_changed_to_analyzed_or_uploaded],
        "Webinar":
            [common_changes_to_notify, has_blacklist_status_changed,
             has_crawling_status_changed_to_analyzed_or_uploaded],
        "ContentItem":
            [common_changes_to_notify, has_blacklist_status_changed,
             has_crawling_status_changed_to_analyzed_or_uploaded],
        "CompanyForEvent":
            [common_changes_to_notify, has_blacklist_status_changed],
        "CompanyForWebinar":
            [common_changes_to_notify, has_blacklist_status_changed],
        "CompanyCompetitor":
            [common_changes_to_notify]
    }

    # Mapping of entity types to the function that returns the object that should be notified on.
    entity_notify_on_mapper = {
        "Event": lambda obj: obj,
        "Company": lambda obj: obj,
        "Webinar": lambda obj: obj,
        "ContentItem": lambda obj: obj.company,
        "CompanyForEvent": lambda obj: obj.event,
        "CompanyForWebinar": lambda obj: obj.webinar,
        "CompanyCompetitor": lambda obj: obj.company,
    }


def notify(entity_obj: EntityType, original_entity_obj: EntityType, entity_type: str):
    """
    Notify external API of changes to the given entity object.
    :param entity_obj: The updated entity object
    :param original_entity_obj: The original entity object
    :param entity_type: Type of the entity, must be one of ENTITY_TYPES
    :return: The object that the notification is sent on
    """
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"{entity_type} not supported, supported entities are: {ENTITY_TYPES}")

    entity_logic = EntityLogic(entity_obj=entity_obj, original_entity_obj=original_entity_obj,
                               entity_type=entity_type)
    if entity_logic.check_if_notify():
        notify_on_obj = entity_logic.notify_on()
        print("Notifying on:", notify_on_obj.__dict__)
        return notify_on_obj
        # TODO: On real API send "requests.post(EXTERNAL_API_URL, json=entity_to_notify_on)"
