import pytest

# Legacy test for deprecated standalone scripts (pre-module refactoring)
# Module structure has replaced standalone scripts: runbooks.inventory.*
# Modern tests exist in tests/inventory/ for current module structure
pytestmark = pytest.mark.skip(reason="Legacy test for deprecated standalone Inventory_Modules script (pre-module refactoring)")

try:
    from common_test_data import (
        AssumeRoleResponseData,
        DescribeOrganizationsResponseData,
        DescribeRegionsResponseData,
        GetCallerIdentity,
        ListAccountsResponseData,
        cli_provided_parameters1,
    )
    from common_test_functions import _amend_make_api_call
    from Inventory_Modules import get_all_credentials
    LEGACY_MODULES_AVAILABLE = True
except ImportError:
    LEGACY_MODULES_AVAILABLE = False
    # Dummy values to prevent NameError
    AssumeRoleResponseData = None
    DescribeOrganizationsResponseData = None
    DescribeRegionsResponseData = None
    GetCallerIdentity = None
    ListAccountsResponseData = None
    cli_provided_parameters1 = None

get_all_credentials_test_result_dict = [
    {"operation_name": "GetCallerIdentity", "test_result": GetCallerIdentity},
    {"operation_name": "DescribeOrganization", "test_result": DescribeOrganizationsResponseData},
    {"operation_name": "AssumeRole", "test_result": AssumeRoleResponseData},
    {"operation_name": "ListAccounts", "test_result": ListAccountsResponseData},
    {"operation_name": "DescribeRegions", "test_result": DescribeRegionsResponseData},
]


# Skipped for now, since I know the get_credential testing needs more work
@pytest.mark.skip
@pytest.mark.parametrize(
    "parameters, test_value_dict",
    [
        (cli_provided_parameters1, get_all_credentials_test_result_dict),
    ],
)
def test_get_all_credentials(parameters, test_value_dict, mocker):
    pProfiles = parameters["pProfiles"]
    pRegionList = parameters["pRegionList"]
    pSkipProfiles = parameters["pSkipProfiles"]
    pSkipAccounts = parameters["pSkipAccounts"]
    pAccountList = parameters["pAccountList"]
    pTiming = parameters["pTiming"]
    pRootOnly = parameters["pRootOnly"]
    pRoleList = parameters["pRoleList"]
    test_data = {"FunctionName": "get_all_credentials", "AccountSpecific": True, "RegionSpecific": True}
    _amend_make_api_call(test_data, test_value_dict, mocker)

    # if isinstance(test_value, Exception):
    # 	print("Expected Error...")
    # 	with pytest.raises(type(test_value)) as error:
    # 		get_all_credentials(pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccountList, pRegionList, pRoleList)
    # 	result = error
    # else:
    result = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccountList, pRegionList, pRoleList
    )
    for cred in result:
        assert cred["Success"]
    print("Result:", result)

    return result
