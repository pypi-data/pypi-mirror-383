# General artifact formatting features
from mcp_server_spira.utils.general import get_execution_status_name


def format_task(task) -> str:
    task_info = f"""
## Task [TK:{task['TaskId']}] - {task['Name']}
{'' if task['Description'] is None else task['Description']}
- **Status:** {task['TaskStatusName']}
- **Type:** {task['TaskTypeName']}
- **Priority:** {task['TaskPriorityName']}
- **Due Date:** {task['EndDate']}
"""
    return task_info

def format_incident(incident) -> str:
    incident_info = f"""
## Incident [IN:{incident['IncidentId']}] - {incident['Name']}
{'' if incident['Description'] is None else incident['Description']}
- **Status:** {incident['IncidentStatusName']}
- **Type:** {incident['IncidentTypeName']}
- **Priority:** {incident['PriorityName']}
- **Severity:** {incident['SeverityName']}
- **Due Date:** {incident['StartDate']}
{'' if incident['DetectedReleaseId'] is None else '- **Detected in Release:** ' + str(incident['DetectedReleaseId'])}
{'' if incident['ResolvedReleaseId'] is None else '- **Planned for Release:** ' + str(incident['ResolvedReleaseId'])}
{'' if incident['VerifiedReleaseId'] is None else '- **Verified in Release:** ' + str(incident['VerifiedReleaseId'])}
"""
    return incident_info

def format_requirement(requirement) -> str:
    requirement_info = f"""
## Requirement [RQ:{requirement['RequirementId']}] - {requirement['Name']}
{'' if requirement['Description'] is None else requirement['Description']}
- **Status:** {requirement['StatusName']}
- **Type:** {requirement['RequirementTypeName']}
- **Importance:** {requirement['ImportanceName']}
- **Release:** {requirement['ReleaseVersionNumber']}
"""
    return requirement_info

def format_test_case(test_case) -> str:
    test_case_info = f"""
## Test Case [TC:{test_case['TestCaseId']}] - {test_case['Name']}
{'' if test_case['Description'] is None else test_case['Description']}
- **Status:** {test_case['TestCaseStatusName']}
- **Type:** {test_case['TestCaseTypeName']}
- **Priority:** {test_case['TestCasePriorityName']}
- **Last Execution Status:** {test_case['ExecutionStatusName']}
- **Last Executed:** {test_case['ExecutionDate']}
"""
    return test_case_info

def format_test_case_folder(test_case_folder) -> str:
    test_case_folder_info = f"""
# Test Folder: {test_case_folder['Name']}
{'' if test_case_folder['Description'] is None else test_case_folder['Description']}
"""
    return test_case_folder_info

def format_test_set(test_set) -> str:
    test_set_info = f"""
## Test Set [TX:{test_set['TestSetId']}] - {test_set['Name']}
{'' if test_set['Description'] is None else test_set['Description']}
- **Status:** {test_set['TestSetStatusName']}
- **Release:** {test_set['ReleaseVersionNumber']}
- **Recurrence:** {test_set['RecurrenceName']}
- **Due Date:** {test_set['PlannedDate']}
"""
    return test_set_info

def format_test_set_folder(test_set_folder) -> str:
    test_set_folder_info = f"""
# Test Set Folder: {test_set_folder['Name']}
{'' if test_set_folder['Description'] is None else test_set_folder['Description']}
"""
    return test_set_folder_info

def format_product(product) -> str:
    product_info = f"""
## Product [PR:{product['ProjectId']}] - {product['Name']}
{'' if product['Description'] is None else product['Description']}
- **Website:** {product['Website']}
- **Template ID:** [PT:{product['ProjectTemplateId']}]
- **Program ID:** [PG:{product['ProjectGroupId']}]
- **% Complete:** {product['PercentComplete']}%
- **Start Date:** {product['StartDate']}
- **End Date:** {product['EndDate']}
"""
    return product_info

def format_product_template(template) -> str:
    template_info = f"""
## Product Template [PT:{template['ProjectTemplateId']}] - {template['Name']}
{'' if template['Description'] is None else template['Description']}
"""
    return template_info

def format_program(program) -> str:
    program_info = f"""
## Program [PG:{program['ProgramId']}] - {program['Name']}
{'' if program['Description'] is None else program['Description']}
- **Website:** {program['Website']}
- **Product Template ID:** [PT:{program['ProjectTemplateId']}]
- **Portfolio ID:** [PF:{program['PortfolioId']}]
"""
    return program_info

def format_milestone(milestone) -> str:
    milestone_info = f"""
## Milestone [GM:{milestone['MilestoneId']}] - {milestone['Name']}
{'' if milestone['Description'] is None else milestone['Description']}
- **Status:** {milestone['StatusName']}
- **Type:** [PT:{milestone['TypeName']}]
- **% Complete:** {milestone['PercentComplete']}%
- **Start Date:** {milestone['StartDate']}
- **End Date:** {milestone['EndDate']}
"""
    return milestone_info

def format_release(release) -> str:
    release_info = f"""
## Release [RL:{release['ReleaseId']}] - {release['Name']}
{'' if release['Description'] is None else release['Description']}
- **Version #:** {release['VersionNumber']}
- **Status:** {release['ReleaseStatusName']}
- **Type:** [PT:{release['ReleaseTypeName']}]
- **% Complete:** {release['PercentComplete']}%
- **Start Date:** {release['StartDate']}
- **End Date:** {release['EndDate']}
"""
    return release_info

def format_risk(risk) -> str:
    risk_info = f"""
## Risk [RK:{risk['RiskId']}] - {risk['Name']}
{'' if risk['Description'] is None else risk['Description']}
- **Status:** {risk['RiskStatusName']}
- **Type:** {risk['RiskTypeName']}
- **Probability:** {risk['RiskProbabilityName']}
- **Impact:** {risk['RiskImpactName']}
- **Exposure:** {risk['RiskExposure']}
- **Review Date:** {risk['ReviewDate']}
"""
    return risk_info

def format_test_run(test_run) -> str:
    test_run_info = f"""
## Test Run [TR:{test_run['TestRunId']}] - {test_run['Name']}
- **Status:** {get_execution_status_name(test_run['ExecutionStatusId'])}
- **Test Case:** TC:{test_run['TestCaseId']}
- **Test Set:** TX:{test_run['TestSetId']}
- **Release:** {test_run['ReleaseVersionNumber']}
- **Start Date:** {test_run['StartDate']}
- **End Date:** {test_run['EndDate']}
"""
    return test_run_info

def format_automation_host(host) -> str:
    host_info = f"""
## Automation Host [AH:{host['AutomationHostId']}] - {host['Name']}
{'' if host['Description'] is None else host['Description']}
- **Token:** {host['Token']}
- **Active:** {host['Active']}
- **Last Contact:** {host['LastContactDate']}
"""
    return host_info

def format_capability(capability) -> str:
    """
    Format a program capability into a readable string.
    
    Args:
        capability: The capability data from the API
        
    Returns:
        Formatted string containing the capability information
    """
    capability_info = f"""
## Capability [CP:{capability['CapabilityId']}] - {capability['Name']}
{'' if capability['Description'] is None else capability['Description']}
- **Status:** {capability['StatusName']}
- **Type:** {capability['TypeName']}
- **Priority:** {capability['PriorityName']}
- **% Complete:** {capability['PercentComplete']}%
- **Milestone:** {capability['MilestoneName']}
- **# Requirements:** {capability['RequirementCount']}
"""
    return capability_info
