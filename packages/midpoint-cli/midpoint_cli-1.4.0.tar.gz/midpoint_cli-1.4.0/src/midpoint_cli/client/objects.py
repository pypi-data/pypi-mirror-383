import itertools
import re
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from textwrap import dedent
from typing import Callable, Optional
from xml.etree.ElementTree import Element

import tabulate
from unidecode import unidecode


def safe_get_text(element: Optional[Element], default: str = '') -> str:
    """Safely get text from an XML element, returning default if element is None."""
    return element.text if element is not None and element.text is not None else default


def safe_get_int(element: Optional[Element], default: int = 0) -> int:
    """Safely get integer from an XML element text, returning default if element is None or text is not a valid int."""
    if element is None or element.text is None:
        return default
    try:
        return int(element.text)
    except (ValueError, TypeError):
        return default


namespaces = {
    'c': 'http://midpoint.evolveum.com/xml/ns/public/common/common-3',
}


class MidpointObject(OrderedDict):
    def get_oid(self) -> Optional[str]:
        oid = self.get('OID')
        return str(oid) if oid is not None else None

    def get_name(self) -> Optional[str]:
        name = self.get('Name')
        return str(name) if name is not None else None


class MidpointObjectList(list[MidpointObject]):
    def find_object(self, search_reference) -> Optional[MidpointObject]:
        for mp_obj in self:
            if search_reference in [mp_obj.get_oid(), mp_obj.get_name()]:
                return mp_obj

        return None

    def filter(self, queryterms: list[str]):
        selected_users = MidpointObjectList()

        for user in self:
            selected = False

            for uservalue in user.values():
                if uservalue is not None:
                    for term in queryterms:
                        if unidecode(term).casefold() in unidecode(uservalue).casefold():
                            selected = True

            if selected:
                selected_users.append(user)

        return selected_users


class MidpointTask(MidpointObject):
    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        name_element = xml_entity.find('c:name', namespaces)
        self['Name'] = name_element.text if name_element is not None else None

        execution_status_entity = xml_entity.find('c:executionStatus', namespaces)

        # Execution status is renamed executionState since Midpoint 4.4
        if execution_status_entity is None:
            execution_status_entity = xml_entity.find('c:executionState', namespaces)

        self['Execution Status'] = execution_status_entity.text if execution_status_entity is not None else 'n/a'

        # Midpoint before version 4.2

        rs = xml_entity.find('c:resultStatus', namespaces)

        # As of Midpoint 4.2, the result has moved

        if rs is None:
            rs = xml_entity.find('c:operationExecution/c:status', namespaces)

        self['Result Status'] = rs.text if rs is not None else ''
        progress = xml_entity.find('c:progress', namespaces)
        self['Progress'] = progress.text if progress is not None else ''
        total = xml_entity.find('c:expectedTotal', namespaces)
        self['Expected Total'] = total.text if total is not None else ''

        # Parse timestamp fields for duration calculation
        self._parse_timestamps(xml_entity)

        # Collect execution statistics

        self._transitions = []
        self._actions = []

        statistics = xml_entity.find('c:activityState/c:activity/c:statistics', namespaces)

        if statistics is not None:
            synchronization = statistics.find('c:synchronization', namespaces)

            for transition in synchronization or []:
                if transition.find('c:onSynchronizationStart', namespaces) is not None:
                    state_start = safe_get_text(transition.find('c:onSynchronizationStart', namespaces))
                    state_end = safe_get_text(transition.find('c:onSynchronizationEnd', namespaces))
                    count = safe_get_int(transition.find('c:counter/c:count', namespaces))
                    self._transitions.append((state_start, state_end, count))

                if transition.find('c:exclusionReason', namespaces) is not None:
                    reason = safe_get_text(transition.find('c:exclusionReason', namespaces))
                    count = safe_get_int(transition.find('c:counter/c:count', namespaces))
                    self._transitions.append((reason, '', count))

            actions_executed = statistics.find('c:actionsExecuted', namespaces)

            for object_actions_entry in actions_executed or []:
                object_type = safe_get_text(object_actions_entry.find('c:objectType', namespaces))
                operation = safe_get_text(object_actions_entry.find('c:operation', namespaces))
                count_success = safe_get_int(object_actions_entry.find('c:totalSuccessCount', namespaces))
                count_failure = safe_get_int(object_actions_entry.find('c:totalFailureCount', namespaces))

                self._actions.append((object_type, operation, count_success, count_failure))

    def _parse_timestamps(self, xml_entity: Element):
        """Parse timestamp fields and calculate execution duration"""
        # Look for various timestamp fields that might indicate start/end times
        start_timestamp = None
        end_timestamp = None

        # Try different timestamp field names based on Midpoint versions
        start_fields = ['c:lastRunStartTimestamp', 'c:startTimestamp']
        end_fields = ['c:lastRunFinishTimestamp', 'c:endTimestamp', 'c:completionTimestamp']

        for field in start_fields:
            elem = xml_entity.find(field, namespaces)
            if elem is not None and elem.text:
                start_timestamp = elem.text
                break

        for field in end_fields:
            elem = xml_entity.find(field, namespaces)
            if elem is not None and elem.text:
                end_timestamp = elem.text
                break

        # Calculate duration if we have both timestamps
        duration = self._calculate_duration(start_timestamp, end_timestamp)
        self['Duration'] = duration if duration else ''

    def _calculate_duration(self, start_timestamp: Optional[str], end_timestamp: Optional[str]) -> Optional[str]:
        """Calculate duration between two timestamps, or elapsed time for running tasks"""
        if not start_timestamp:
            return None

        try:
            # Parse timestamps - handle both with and without microseconds
            start_formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%f%z',
                '%Y-%m-%dT%H:%M:%S%z',
            ]

            start_dt = None
            end_dt = None

            for fmt in start_formats:
                try:
                    start_dt = datetime.strptime(start_timestamp, fmt)
                    break
                except ValueError:
                    continue

            if not start_dt:
                return None

            # If we have an end timestamp, calculate duration between start and end
            if end_timestamp:
                for fmt in start_formats:
                    try:
                        end_dt = datetime.strptime(end_timestamp, fmt)
                        break
                    except ValueError:
                        continue

                if end_dt:
                    duration_seconds = (end_dt - start_dt).total_seconds()
                    return self._format_duration(duration_seconds)
            else:
                # No end timestamp - task is still running, calculate elapsed time from start to now
                # Check if task is actually running by checking execution status
                if self.get('Execution Status') in ['RUNNING', 'RUNNABLE']:
                    now = datetime.utcnow()
                    duration_seconds = (now - start_dt).total_seconds()
                    return self._format_duration(duration_seconds)

        except (ValueError, TypeError):
            pass

        return None

    def _format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable format"""
        if seconds < 0:
            return '0s'

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)

        if hours > 0:
            return f'{hours}h {minutes}m {remaining_seconds}s'
        elif minutes > 0:
            return f'{minutes}m {remaining_seconds}s'
        else:
            return f'{remaining_seconds}s'

    def get_transitions(self):
        return self._transitions

    def get_actions(self):
        return self._actions

    def get_full_description(self):
        text = dedent("""\
            {}

            Transitions
            {}

            Actions
            {}
        """).format(
            tabulate.tabulate(self.items()),
            tabulate.tabulate(self.get_transitions(), headers=['From State', 'To State', 'Count']),
            tabulate.tabulate(self.get_actions(), headers=['Type', 'Action', 'Count Success', 'Count Failure']),
        )

        return text


class MidpointResource(MidpointObject):
    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = safe_get_text(xml_entity.find('c:name', namespaces))
        self['Availability Status'] = optional_text(
            xml_entity.find('c:operationalState/c:lastAvailabilityStatus', namespaces)
        )
        connector_ref = xml_entity.find('c:connectorRef', namespaces)
        self['connectorRef'] = connector_ref.attrib['oid'] if connector_ref is not None else None


class MidpointConnector(MidpointObject):
    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Connector type'] = safe_get_text(xml_entity.find('c:connectorType', namespaces))
        self['Version'] = safe_get_text(xml_entity.find('c:connectorVersion', namespaces))


class MidpointUser(MidpointObject):
    @staticmethod
    def strip_namespace(tag: str) -> str:
        return re.sub(r'{.*}', '', tag)

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = safe_get_text(xml_entity.find('c:name', namespaces))
        self['Title'] = optional_text(xml_entity.find('c:title', namespaces))
        self['FullName'] = optional_text(xml_entity.find('c:fullName', namespaces))
        self['Status'] = safe_get_text(xml_entity.find('c:activation/c:effectiveStatus', namespaces))
        self['EmpNo'] = optional_text(xml_entity.find('c:employeeNumber', namespaces))
        self['Email'] = optional_text(xml_entity.find('c:emailAddress', namespaces))
        self['OU'] = optional_text(xml_entity.find('c:organizationalUnit', namespaces))

        activation = xml_entity.find('c:activation', namespaces)
        extfields = xml_entity.find('c:extension', namespaces)

        self._all_attributes = []

        for child in itertools.chain(xml_entity, activation or [], extfields or []):
            # Check if the child has no children and contains non-empty text
            if len(child) == 0 and (child.text is not None and child.text.strip()):
                self._all_attributes.append((self.strip_namespace(child.tag), child.text))

    def get_all_attributes(self):
        return self._all_attributes


class MidpointOrganization(MidpointObject):
    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = safe_get_text(xml_entity.find('c:name', namespaces))
        self['DisplayName'] = optional_text(xml_entity.find('c:displayName', namespaces))
        self['Status'] = safe_get_text(xml_entity.find('c:activation/c:effectiveStatus', namespaces))
        parentorg = xml_entity.find('c:parentOrgRef', namespaces)
        self['Parent'] = None if parentorg is None else parentorg.attrib['oid']


@dataclass
class MidpointObjectType:
    object_type: Optional[str]
    endpoint: Optional[str]
    tagname: str


class MidpointTypeNotFound(Exception):
    pass


class MidpointObjectTypes(Enum):
    CONNECTOR = MidpointObjectType('ConnectorType', 'connectors', 'connector')
    CONNECTOR_HOST = MidpointObjectType('ConnectorHostType', 'connectorHosts', 'connectorHost')
    GENERIC_OBJECT = MidpointObjectType('GenericObjectType', 'genericObjects', 'genericObject')
    RESOURCE = MidpointObjectType('ResourceType', 'resources', 'resource')
    USER = MidpointObjectType('UserType', 'users', 'user')
    OBJECT_TEMPLATE = MidpointObjectType('ObjectTemplateType', 'objectTemplates', 'objectTemplate')
    SYSTEM_CONFIGURATION = MidpointObjectType('SystemConfigurationType', 'systemConfigurations', 'systemConfiguration')
    TASK = MidpointObjectType('TaskType', 'tasks', 'task')
    SHADOW = MidpointObjectType('ShadowType', 'shadows', 'shadow')
    ROLE = MidpointObjectType('RoleType', 'roles', 'role')
    VALUE_POLICY = MidpointObjectType('ValuePolicyType', 'valuePolicies', 'valuePolicy')
    ORG = MidpointObjectType('OrgType', 'orgs', 'org')
    FUNCTION_LIBRARY = MidpointObjectType('FunctionLibraryType', 'functionLibraries', 'functionLibrary')
    OBJECTS = MidpointObjectType(None, None, 'objects')

    @staticmethod
    def __find(needle: str, getter: Callable) -> MidpointObjectType:
        for type in MidpointObjectTypes:
            if getter(type.value) == needle:
                return type.value

        raise MidpointTypeNotFound(f'No type found for value {needle}')

    @staticmethod
    def find_by_java_type(java_type: str) -> MidpointObjectType:
        return MidpointObjectTypes.__find(java_type, lambda t: t.object_type)

    @staticmethod
    def find_by_endpoint(endpoint: str) -> MidpointObjectType:
        return MidpointObjectTypes.__find(endpoint, lambda t: t.endpoint)

    @staticmethod
    def find_by_tagname(tagname: str) -> MidpointObjectType:
        return MidpointObjectTypes.__find(tagname, lambda t: t.tagname)


def optional_text(node: Optional[Element]) -> Optional[str]:
    return node.text if node is not None else None
