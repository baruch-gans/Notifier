The EntitiesLogic class is a module that checks if a notification needs to be sent for certain changes made to certain entities.

It takes in the current and original entity objects, as well as the entity type as inputs in its initialization. 

The class contains several methods, including check_if_notify(), notify_on(), and several other methods that check for specific changes in the entity that would trigger a notification. These methods utilize dictionaries entity_checks_mapper and entity_notify_on_mapper to map the entity types to the corresponding check functions and notify-on functions. The EXTERNAL_API_URL variable is also defined, which is the endpoint of an external API that will be notified when a change in the entity meets the specified criteria.
