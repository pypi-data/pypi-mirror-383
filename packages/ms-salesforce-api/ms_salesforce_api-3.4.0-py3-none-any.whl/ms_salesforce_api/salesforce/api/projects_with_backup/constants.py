DEFAULT_PROJECTS_QUERY = """
SELECT
    Id,
    Account.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.Name,
    Account.Name,
    FRM_ProjectName__c,
    FRM_ProjectCode__c,
    Tolabel(PCK_ProjectStatus__c),
    DT_ProjectStartDate__c,
    DT_ProjectEndDate__c,
    LKP_AccountManager__r.Name,
    Account_Billing_Country__c,
    PCK_Division__c
FROM
    Opportunity
"""
