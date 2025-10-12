from fbnconfig import Deployment, datatype, fund_accounting, posting_module, property

"""
An example configuration for defining fund accounting related entities.
The script configures the following entities:
- Chart of accounts
- Accounts within a chart of account
- Posting module
"""


def configure(env):

    rating = property.DefinitionResource(
        id="rating",
        domain=property.Domain.ChartOfAccounts,
        scope="sc1",
        code="rating",
        display_name="Rating",
        data_type_id=datatype.DataTypeRef(id="default_str", scope="system", code="string"),
        constraint_style=property.ConstraintStyle.Collection,
        property_description="Example property representing a rating",
        life_time=property.LifeTime.Perpetual,
        collection_type=property.CollectionType.Array,
    )

    chart_property = fund_accounting.PropertyValue(
        property_key=rating,
        label_value="Example_label"
    )

    chart_of_account = fund_accounting.ChartOfAccountsResource(
        id="example_chart",
        scope="example_scope",
        code="example_code",
        display_name="example_display_name",
        description="example_description",
        properties=[chart_property]
    )

    instrument_property_definition = property.DefinitionResource(
        id="pd1",
        domain=property.Domain.Account,
        scope="sc1",
        code="pd1",
        display_name="Property definition example",
        data_type_id=property.ResourceId(scope="system", code="number"),
        constraint_style=property.ConstraintStyle.Property,
        property_description="Example property definition",
        life_time=property.LifeTime.Perpetual,
        collection_type=None,
    )

    account_property = fund_accounting.PropertyValue(
        property_key=instrument_property_definition,
        label_value="Goodbye"
    )

    account = fund_accounting.AccountResource(
        id="example_account",
        chart_of_accounts=chart_of_account,
        code="account_code",
        description="example_desc",
        type=fund_accounting.AccountType.ASSET,
        status=fund_accounting.AccountStatus.ACTIVE,
        control="Manual",
        properties=[account_property]
    )

    rule = posting_module.PostingModuleRule(
        rule_id="example_rule",
        general_ledger_account_code=account,
        rule_filter="SourceType eq 'LusidTransaction'"
    )

    posting_mod = posting_module.PostingModuleResource(
        id="posting_module_id",
        chart_of_accounts=chart_of_account,
        code="module_code",
        display_name="example_display_name",
        description="example_description",
        rules=[rule]
    )

    return Deployment("fund_accounting_example", [chart_of_account, account, posting_mod])
