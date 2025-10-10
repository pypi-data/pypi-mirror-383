from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class LeaveEntitlementGet(BrynQPanderaDataFrameModel):
    """
    Schema for hr2d__LeaveEntitlement__c entity GET operations.
    Represents leave entitlement records in HR2Day system.
    """

    # Standard Salesforce fields
    id: Series[str] = pa.Field(alias="Id", description="Record ID", coerce=True)
    name: Series[str] = pa.Field(alias="Name", description="Leave year", coerce=True)
    created_by_id: Series[str] = pa.Field(alias="CreatedById", description="Created By ID", coerce=True)
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", description="Created Date", coerce=True)
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", description="Last Modified By ID", coerce=True)
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", description="Last Modified Date", coerce=True)
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", description="System Modstamp", coerce=True)

    # Basic fields
    employment_sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__ArbrelVolgnr__c", nullable=True, description="Employment sequence number", coerce=True)
    balance_total: Optional[Series[float]] = pa.Field(alias="hr2d__BalanceTotal__c", nullable=True, description="Balance (total)", coerce=True)
    employee: Optional[Series[str]] = pa.Field(alias="hr2d__Employee__c", nullable=True, description="Employee", coerce=True)
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__EndDate__c", nullable=True, description="End date period", coerce=True)
    is_import_record: Optional[Series[bool]] = pa.Field(alias="hr2d__IsImportRecord__c", nullable=True, description="Import record", coerce=True)
    key: Optional[Series[str]] = pa.Field(alias="hr2d__Key__c", nullable=True, description="Key", coerce=True)
    notes: Optional[Series[str]] = pa.Field(alias="hr2d__Notes__c", nullable=True, description="Notes", coerce=True)
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__StartDate__c", nullable=True, description="Start date period", coerce=True)

    # Time in lieu (TVT) fields
    time_in_lieu_balance: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_Balance__c", nullable=True, description="Time in lieu balance", coerce=True)
    time_in_lieu_correction: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_Correction__c", nullable=True, description="Time in lieu correction", coerce=True)
    time_in_lieu_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_Entitlement__c", nullable=True, description="Time in lieu accrual", coerce=True)
    time_in_lieu_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_PayBuy__c", nullable=True, description="Time in lieu Pay/Buy", coerce=True)
    time_in_lieu_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_StartBalance__c", nullable=True, description="Time in lieu opening balance", coerce=True)
    time_in_lieu_taken: Optional[Series[float]] = pa.Field(alias="hr2d__Tvt_Taken__c", nullable=True, description="Time in lieu taken", coerce=True)

    # L1 Leave Type fields
    l1_accrual: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Accrual__c", nullable=True, description="Leave1 Accrual", coerce=True)
    l1_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Balance__c", nullable=True, description="Leave1 Balance", coerce=True)
    l1_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Correction__c", nullable=True, description="Leave1 Correction", coerce=True)
    l1_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Entitlement__c", nullable=True, description="Leave1 Entitlement", coerce=True)
    l1_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L1_EntitlementFulltime__c", nullable=True, description="Leave1 Fulltime entitlement", coerce=True)
    l1_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L1_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 1", coerce=True)
    l1_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L1_EntitlementText__c", nullable=True, description="Explanation entitlement 1", coerce=True)
    l1_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L1_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 1", coerce=True)
    l1_entitlement_next_year_text: Optional[Series[str]] = pa.Field(alias="hr2d__L1_EntNextYearText__c", nullable=True, description="Explanation entitlement next calendar year", coerce=True)
    l1_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L1_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 1", coerce=True)
    l1_entitlement_this_year_text: Optional[Series[str]] = pa.Field(alias="hr2d__L1_EntThisYearText__c", nullable=True, description="Explanation entitlement this calendar year", coerce=True)
    l1_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L1_ExpirationDateOverrides__c", nullable=True, description="Leave1 Expiration date overrides", coerce=True)
    l1_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Expired__c", nullable=True, description="Leave1 Deprecated", coerce=True)
    l1_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L1_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 1", coerce=True)
    l1_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L1_MaxBalance__c", nullable=True, description="Leave1 Maximum balance", coerce=True)
    l1_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L1_PayBuy__c", nullable=True, description="Leave1 Sell/Buy", coerce=True)
    l1_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L1_StartBalance__c", nullable=True, description="Leave1 Opening balance", coerce=True)
    l1_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L1_Taken__c", nullable=True, description="Leave1 Taken", coerce=True)
    l1_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L1_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 1", coerce=True)
    l1_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L1_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 1", coerce=True)
    l1_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L1_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 1", coerce=True)
    l1_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L1_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 1", coerce=True)

    # L2 Leave Type fields
    l2_accrual: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Accrual__c", nullable=True, description="Leave2 Accrual", coerce=True)
    l2_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Balance__c", nullable=True, description="Leave2 Balance", coerce=True)
    l2_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Correction__c", nullable=True, description="Leave2 Correction", coerce=True)
    l2_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Entitlement__c", nullable=True, description="Leave2 Entitlement", coerce=True)
    l2_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L2_EntitlementFulltime__c", nullable=True, description="Leave2 Fulltime entitlement", coerce=True)
    l2_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L2_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 2", coerce=True)
    l2_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L2_EntitlementText__c", nullable=True, description="Explanation entitlement 2", coerce=True)
    l2_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L2_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 2", coerce=True)
    l2_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L2_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 2", coerce=True)
    l2_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L2_ExpirationDateOverrides__c", nullable=True, description="Leave2 Expiration date overrides", coerce=True)
    l2_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Expired__c", nullable=True, description="Leave2 Deprecated", coerce=True)
    l2_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L2_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 2", coerce=True)
    l2_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L2_MaxBalance__c", nullable=True, description="Leave2 Maximum balance", coerce=True)
    l2_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L2_PayBuy__c", nullable=True, description="Leave2 Sell/Buy", coerce=True)
    l2_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L2_StartBalance__c", nullable=True, description="Leave2 Opening balance", coerce=True)
    l2_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L2_Taken__c", nullable=True, description="Leave2 Taken", coerce=True)
    l2_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L2_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 2", coerce=True)
    l2_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L2_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 2", coerce=True)
    l2_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L2_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 2", coerce=True)
    l2_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L2_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 2", coerce=True)

    # L3 Leave Type fields
    l3_accrual: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Accrual__c", nullable=True, description="Leave3 Accrual", coerce=True)
    l3_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Balance__c", nullable=True, description="Leave3 Balance", coerce=True)
    l3_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Correction__c", nullable=True, description="Leave3 Correction", coerce=True)
    l3_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Entitlement__c", nullable=True, description="Leave3 Entitlement", coerce=True)
    l3_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L3_EntitlementFulltime__c", nullable=True, description="Leave3 Fulltime entitlement", coerce=True)
    l3_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L3_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 3", coerce=True)
    l3_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L3_EntitlementText__c", nullable=True, description="Explanation entitlement 3", coerce=True)
    l3_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L3_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 3", coerce=True)
    l3_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L3_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 3", coerce=True)
    l3_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L3_ExpirationDateOverrides__c", nullable=True, description="Leave3 Expiration date overrides", coerce=True)
    l3_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Expired__c", nullable=True, description="Leave3 Deprecated", coerce=True)
    l3_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L3_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 3", coerce=True)
    l3_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L3_MaxBalance__c", nullable=True, description="Leave3 Maximum balance", coerce=True)
    l3_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L3_PayBuy__c", nullable=True, description="Leave3 Sell/Buy", coerce=True)
    l3_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L3_StartBalance__c", nullable=True, description="Leave3 Opening balance", coerce=True)
    l3_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L3_Taken__c", nullable=True, description="Leave3 Taken", coerce=True)
    l3_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L3_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 3", coerce=True)
    l3_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L3_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 3", coerce=True)
    l3_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L3_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 3", coerce=True)
    l3_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L3_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 3", coerce=True)

    # L4 Leave Type fields
    l4_accrual: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Accrual__c", nullable=True, description="Leave4 Accrual", coerce=True)
    l4_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Balance__c", nullable=True, description="Leave4 Balance", coerce=True)
    l4_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Correction__c", nullable=True, description="Leave4 Correction", coerce=True)
    l4_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Entitlement__c", nullable=True, description="Leave4 Entitlement", coerce=True)
    l4_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L4_EntitlementFulltime__c", nullable=True, description="Leave4 Fulltime entitlement", coerce=True)
    l4_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L4_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 4", coerce=True)
    l4_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L4_EntitlementText__c", nullable=True, description="Explanation entitlement 4", coerce=True)
    l4_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L4_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 4", coerce=True)
    l4_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L4_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 4", coerce=True)
    l4_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L4_ExpirationDateOverrides__c", nullable=True, description="Leave4 Expiration date overrides", coerce=True)
    l4_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Expired__c", nullable=True, description="Leave4 Deprecated", coerce=True)
    l4_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L4_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 4", coerce=True)
    l4_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L4_MaxBalance__c", nullable=True, description="Leave4 Maximum balance", coerce=True)
    l4_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L4_PayBuy__c", nullable=True, description="Leave4 Sell/Buy", coerce=True)
    l4_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L4_StartBalance__c", nullable=True, description="Leave4 Opening balance", coerce=True)
    l4_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L4_Taken__c", nullable=True, description="Leave4 Taken", coerce=True)
    l4_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L4_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 4", coerce=True)
    l4_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L4_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 4", coerce=True)
    l4_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L4_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 4", coerce=True)
    l4_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L4_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 4", coerce=True)

    # L5 Leave Type fields
    l5_accrual: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Accrual__c", nullable=True, description="Leave5 Accrual", coerce=True)
    l5_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Balance__c", nullable=True, description="Leave5 Balance", coerce=True)
    l5_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Correction__c", nullable=True, description="Leave5 Correction", coerce=True)
    l5_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Entitlement__c", nullable=True, description="Leave5 Entitlement", coerce=True)
    l5_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L5_EntitlementFulltime__c", nullable=True, description="Leave5 Fulltime entitlement", coerce=True)
    l5_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L5_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 5", coerce=True)
    l5_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L5_EntitlementText__c", nullable=True, description="Explanation entitlement 5", coerce=True)
    l5_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L5_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 5", coerce=True)
    l5_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L5_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 5", coerce=True)
    l5_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L5_ExpirationDateOverrides__c", nullable=True, description="Leave5 Expiration date overrides", coerce=True)
    l5_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Expired__c", nullable=True, description="Leave5 Deprecated", coerce=True)
    l5_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L5_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 5", coerce=True)
    l5_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L5_MaxBalance__c", nullable=True, description="Leave5 Maximum balance", coerce=True)
    l5_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L5_PayBuy__c", nullable=True, description="Leave5 Sell/Buy", coerce=True)
    l5_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L5_StartBalance__c", nullable=True, description="Leave5 Opening balance", coerce=True)
    l5_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L5_Taken__c", nullable=True, description="Leave5 Taken", coerce=True)
    l5_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L5_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 5", coerce=True)
    l5_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L5_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 5", coerce=True)
    l5_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L5_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 5", coerce=True)
    l5_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L5_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 5", coerce=True)

    # L11 Leave Type fields
    l11_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L11_Balance__c", nullable=True, description="Leave11 Balance", coerce=True)
    l11_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L11_Correction__c", nullable=True, description="Leave11 Correction", coerce=True)
    l11_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L11_Entitlement__c", nullable=True, description="Leave11 Entitlement", coerce=True)
    l11_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L11_EntitlementFulltime__c", nullable=True, description="Leave11 Fulltime entitlement", coerce=True)
    l11_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L11_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 11", coerce=True)
    l11_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L11_EntitlementText__c", nullable=True, description="Explanation entitlement 11", coerce=True)
    l11_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L11_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 11", coerce=True)
    l11_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L11_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 11", coerce=True)
    l11_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L11_ExpirationDateOverrides__c", nullable=True, description="Leave11 Expiration date overrides", coerce=True)
    l11_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L11_Expired__c", nullable=True, description="Leave11 Deprecated", coerce=True)
    l11_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L11_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 11", coerce=True)
    l11_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L11_MaxBalance__c", nullable=True, description="Leave11 Maximum balance", coerce=True)
    l11_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L11_PayBuy__c", nullable=True, description="Leave11 Sell/Buy", coerce=True)
    l11_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L11_StartBalance__c", nullable=True, description="Leave11 Opening balance", coerce=True)
    l11_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L11_Taken__c", nullable=True, description="Leave11 Taken", coerce=True)
    l11_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L11_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 11", coerce=True)
    l11_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L11_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 11", coerce=True)
    l11_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L11_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 11", coerce=True)
    l11_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L11_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 11", coerce=True)

    # L12 Leave Type fields
    l12_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L12_Balance__c", nullable=True, description="Leave12 Balance", coerce=True)
    l12_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L12_Correction__c", nullable=True, description="Leave12 Correction", coerce=True)
    l12_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L12_Entitlement__c", nullable=True, description="Leave12 Entitlement", coerce=True)
    l12_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L12_EntitlementFulltime__c", nullable=True, description="Leave12 Fulltime entitlement", coerce=True)
    l12_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L12_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 12", coerce=True)
    l12_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L12_EntitlementText__c", nullable=True, description="Explanation entitlement 12", coerce=True)
    l12_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L12_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 12", coerce=True)
    l12_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L12_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 12", coerce=True)
    l12_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L12_ExpirationDateOverrides__c", nullable=True, description="Leave12 Expiration date overrides", coerce=True)
    l12_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L12_Expired__c", nullable=True, description="Leave12 Deprecated", coerce=True)
    l12_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L12_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 12", coerce=True)
    l12_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L12_MaxBalance__c", nullable=True, description="Leave12 Maximum balance", coerce=True)
    l12_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L12_PayBuy__c", nullable=True, description="Leave12 Sell/Buy", coerce=True)
    l12_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L12_StartBalance__c", nullable=True, description="Leave12 Opening balance", coerce=True)
    l12_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L12_Taken__c", nullable=True, description="Leave12 Taken", coerce=True)
    l12_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L12_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 12", coerce=True)
    l12_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L12_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 12", coerce=True)
    l12_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L12_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 12", coerce=True)
    l12_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L12_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 12", coerce=True)

    # L13 Leave Type fields
    l13_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L13_Balance__c", nullable=True, description="Leave13 Balance", coerce=True)
    l13_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L13_Correction__c", nullable=True, description="Leave13 Correction", coerce=True)
    l13_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L13_Entitlement__c", nullable=True, description="Leave13 Entitlement", coerce=True)
    l13_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L13_EntitlementFulltime__c", nullable=True, description="Leave13 Fulltime entitlement", coerce=True)
    l13_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L13_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 13", coerce=True)
    l13_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L13_EntitlementText__c", nullable=True, description="Explanation entitlement 13", coerce=True)
    l13_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L13_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 13", coerce=True)
    l13_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L13_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 13", coerce=True)
    l13_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L13_ExpirationDateOverrides__c", nullable=True, description="Leave13 Expiration date overrides", coerce=True)
    l13_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L13_Expired__c", nullable=True, description="Leave13 Deprecated", coerce=True)
    l13_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L13_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 13", coerce=True)
    l13_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L13_MaxBalance__c", nullable=True, description="Leave13 Maximum balance", coerce=True)
    l13_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L13_PayBuy__c", nullable=True, description="Leave13 Sell/Buy", coerce=True)
    l13_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L13_StartBalance__c", nullable=True, description="Leave13 Opening balance", coerce=True)
    l13_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L13_Taken__c", nullable=True, description="Leave13 Taken", coerce=True)
    l13_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L13_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 13", coerce=True)
    l13_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L13_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 13", coerce=True)
    l13_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L13_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 13", coerce=True)
    l13_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L13_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 13", coerce=True)

    # L14 Leave Type fields
    l14_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L14_Balance__c", nullable=True, description="Leave14 Balance", coerce=True)
    l14_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L14_Correction__c", nullable=True, description="Leave14 Correction", coerce=True)
    l14_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L14_Entitlement__c", nullable=True, description="Leave14 Entitlement", coerce=True)
    l14_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L14_EntitlementFulltime__c", nullable=True, description="Leave14 Fulltime entitlement", coerce=True)
    l14_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L14_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 14", coerce=True)
    l14_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L14_EntitlementText__c", nullable=True, description="Explanation entitlement 14", coerce=True)
    l14_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L14_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 14", coerce=True)
    l14_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L14_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 14", coerce=True)
    l14_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L14_ExpirationDateOverrides__c", nullable=True, description="Leave14 Expiration date overrides", coerce=True)
    l14_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L14_Expired__c", nullable=True, description="Leave14 Deprecated", coerce=True)
    l14_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L14_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 14", coerce=True)
    l14_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L14_MaxBalance__c", nullable=True, description="Leave14 Maximum balance", coerce=True)
    l14_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L14_PayBuy__c", nullable=True, description="Leave14 Sell/Buy", coerce=True)
    l14_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L14_StartBalance__c", nullable=True, description="Leave14 Opening balance", coerce=True)
    l14_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L14_Taken__c", nullable=True, description="Leave14 Taken", coerce=True)
    l14_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L14_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 14", coerce=True)
    l14_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L14_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 14", coerce=True)
    l14_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L14_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 14", coerce=True)
    l14_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L14_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 14", coerce=True)

    # L15 Leave Type fields
    l15_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L15_Balance__c", nullable=True, description="Leave15 Balance", coerce=True)
    l15_correction: Optional[Series[float]] = pa.Field(alias="hr2d__L15_Correction__c", nullable=True, description="Leave15 Correction", coerce=True)
    l15_entitlement: Optional[Series[float]] = pa.Field(alias="hr2d__L15_Entitlement__c", nullable=True, description="Leave15 Entitlement", coerce=True)
    l15_entitlement_fulltime: Optional[Series[float]] = pa.Field(alias="hr2d__L15_EntitlementFulltime__c", nullable=True, description="Leave15 Fulltime entitlement", coerce=True)
    l15_entitlement_simple_text: Optional[Series[str]] = pa.Field(alias="hr2d__L15_EntitlementSimpleText__c", nullable=True, description="Short explanation entitlements 15", coerce=True)
    l15_entitlement_text: Optional[Series[str]] = pa.Field(alias="hr2d__L15_EntitlementText__c", nullable=True, description="Explanation entitlement 15", coerce=True)
    l15_entitlement_next_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L15_EntNextCalYear__c", nullable=True, description="Entitlement next calendar year 15", coerce=True)
    l15_entitlement_this_cal_year: Optional[Series[float]] = pa.Field(alias="hr2d__L15_EntThisCalYear__c", nullable=True, description="Entitlement this calendar year 15", coerce=True)
    l15_expiration_date_overrides: Optional[Series[str]] = pa.Field(alias="hr2d__L15_ExpirationDateOverrides__c", nullable=True, description="Leave15 Expiration date overrides", coerce=True)
    l15_expired: Optional[Series[float]] = pa.Field(alias="hr2d__L15_Expired__c", nullable=True, description="Leave15 Deprecated", coerce=True)
    l15_historical_data: Optional[Series[str]] = pa.Field(alias="hr2d__L15_HistoricalData__c", nullable=True, description="Verlofgegevens per kalenderjaar 15", coerce=True)
    l15_max_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L15_MaxBalance__c", nullable=True, description="Leave15 Maximum balance", coerce=True)
    l15_pay_buy: Optional[Series[float]] = pa.Field(alias="hr2d__L15_PayBuy__c", nullable=True, description="Leave15 Sell/Buy", coerce=True)
    l15_start_balance: Optional[Series[float]] = pa.Field(alias="hr2d__L15_StartBalance__c", nullable=True, description="Leave15 Opening balance", coerce=True)
    l15_taken: Optional[Series[float]] = pa.Field(alias="hr2d__L15_Taken__c", nullable=True, description="Leave15 Taken", coerce=True)
    l15_taken_next_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L15_TakenNextH1__c", nullable=True, description="Taken next 1st half of year 15", coerce=True)
    l15_taken_next_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L15_TakenNextH2__c", nullable=True, description="Taken next 2nd half of year 15", coerce=True)
    l15_taken_this_h1: Optional[Series[float]] = pa.Field(alias="hr2d__L15_TakenThisH1__c", nullable=True, description="Taken this 1st half of year 15", coerce=True)
    l15_taken_this_h2: Optional[Series[float]] = pa.Field(alias="hr2d__L15_TakenThisH2__c", nullable=True, description="Taken this 2nd half of year 15", coerce=True)

    class Config:
        """Pandera configuration"""
        strict = "filter"
        add_missing_columns = True
        coerce = True

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employee": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }
