from datetime import datetime, date
from typing import Optional
from pandera.typing import Series
import pandera as pa
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class PayrollGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Verloning__c entity in HR2Day. Represents a payroll record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=False, coerce=True, description="Record ID")
    name: Series[str] = pa.Field(alias="Name", nullable=True, coerce=True, description="Payroll name")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # Basic Information Fields
    employee: Series[str] = pa.Field(alias="hr2d__Employee__c", nullable=True, coerce=True, description="Employee")
    employer: Series[str] = pa.Field(alias="hr2d__Employer__c", nullable=True, coerce=True, description="Employer")
    employment_relationship: Series[str] = pa.Field(alias="hr2d__Arbeidsrelatie__c", nullable=True, coerce=True, description="Employment relationship for this payroll")
    year: Series[str] = pa.Field(alias="hr2d__Jaar__c", nullable=True, coerce=True, description="Year of payroll")
    period: Series[str] = pa.Field(alias="hr2d__Periode__c", nullable=True, coerce=True, description="Payroll period (month or other period)")
    period_nr: Series[float] = pa.Field(alias="hr2d__PeriodeNr__c", nullable=True, coerce=True, description="Period number")
    valid: Series[bool] = pa.Field(alias="hr2d__Geldig__c", nullable=True, coerce=True, description="If enabled, this is the currently valid record")
    key: Series[str] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Key field consisting of employer tax number, employee BSN, employment number, year/period")
    version: Series[float] = pa.Field(alias="hr2d__Versie__c", nullable=True, coerce=True, description="Version of this payroll record")
    paid: Series[str] = pa.Field(alias="hr2d__Verloond__c", nullable=True, coerce=True, description="Indicates if this is an actual payroll or dummy record")
    inactive: Series[bool] = pa.Field(alias="hr2d__Inactief__c", nullable=True, coerce=True, description="Payroll for inactive employee")
    multi_employment: Series[str] = pa.Field(alias="hr2d__Multi_DV__c", nullable=True, coerce=True, description="Multiple employment relationships")
    sector_fund: Series[str] = pa.Field(alias="hr2d__Sectorfonds__c", nullable=True, coerce=True, description="Sector for social insurance premiums")
    sector_risk_group: Series[str] = pa.Field(alias="hr2d__SectorRisGrp__c", nullable=True, coerce=True, description="Risk group within sector")
    fiscal_regulation: Series[str] = pa.Field(alias="hr2d__FiscaleRegeling__c", nullable=True, coerce=True, description="Fiscal arrangements")
    payslip_text: Series[str] = pa.Field(alias="hr2d__PayslipText__c", nullable=True, coerce=True, description="Individual payslip note/explanation")
    salary_spec: Series[str] = pa.Field(alias="hr2d__SalarisSpec__c", nullable=True, coerce=True, description="Payslip identifier")
    parameters: Series[str] = pa.Field(alias="hr2d__Parameters__c", nullable=True, coerce=True, description="Applied parameters record")

    # Date Fields
    period_start_date: Series[date] = pa.Field(alias="hr2d__Periode_datum__c", nullable=True, coerce=True, description="Start date of accounting period")
    period_end_date: Series[date] = pa.Field(alias="hr2d__Periode_einddatum__c", nullable=True, coerce=True, description="End date of accounting period")
    employment_start: Series[date] = pa.Field(alias="hr2d__Aanvang_Arbrel__c", nullable=True, coerce=True, description="Start of employment relationship")
    employment_end: Series[date] = pa.Field(alias="hr2d__Einde_Arbrel__c", nullable=True, coerce=True, description="End of employment relationship")
    last_calculated_date: Series[datetime] = pa.Field(alias="hr2d__LaatstBerekendDatum__c", nullable=True, coerce=True, description="Time when payroll was last calculated")
    last_renewed_date: Series[datetime] = pa.Field(alias="hr2d__LaatstVernieuwdDatum__c", nullable=True, coerce=True, description="Time when payroll was last renewed")
    payroll_until: Series[date] = pa.Field(alias="hr2d__Verlonen_tot__c", nullable=True, coerce=True, description="Date until which employee should be processed after termination")

    # Salary Fields
    salary: Series[float] = pa.Field(alias="hr2d__Salaris__c", nullable=True, coerce=True, description="Salary at end of period")
    salary_fulltime: Series[float] = pa.Field(alias="hr2d__Salaris_Fulltime__c", nullable=True, coerce=True, description="Full-time salary at end of period")
    hourly_wage: Series[float] = pa.Field(alias="hr2d__Uurloon__c", nullable=True, coerce=True, description="Hourly wage")
    hourly_wage_2: Series[float] = pa.Field(alias="hr2d__Uurloon2__c", nullable=True, coerce=True, description="Second hourly wage")
    hourly_wage_3: Series[float] = pa.Field(alias="hr2d__Uurloon3__c", nullable=True, coerce=True, description="Third hourly wage")
    gross: Series[float] = pa.Field(alias="hr2d__Bruto__c", nullable=True, coerce=True, description="Total taxable wage components")
    net: Series[float] = pa.Field(alias="hr2d__Netto__c", nullable=True, coerce=True, description="Net wage")
    payment: Series[float] = pa.Field(alias="hr2d__Uitbetalen__c", nullable=True, coerce=True, description="Total payment amount")
    payment_bank_2: Series[float] = pa.Field(alias="hr2d__Uitbetalen_Bank2__c", nullable=True, coerce=True, description="Amount paid to second bank account")
    minimum_wage: Series[float] = pa.Field(alias="hr2d__Minimumloon__c", nullable=True, coerce=True, description="Minimum wage on full-time basis")
    costs_reservations: Series[float] = pa.Field(alias="hr2d__KostenReserveringen__c", nullable=True, coerce=True, description="Total costs based on period payments and reservations")
    costs_actual: Series[float] = pa.Field(alias="hr2d__KostenWerkelijk__c", nullable=True, coerce=True, description="Total costs based on actual payments")

    # Working Time Fields
    calendar_days: Series[float] = pa.Field(alias="hr2d__Kalenderdagen__c", nullable=True, coerce=True, description="Number of active calendar days in period")
    working_days: Series[float] = pa.Field(alias="hr2d__Werkdagen__c", nullable=True, coerce=True, description="Number of active working days in period")
    schedule_days: Series[float] = pa.Field(alias="hr2d__Roosterdagen__c", nullable=True, coerce=True, description="Number of worked days according to schedule")
    schedule_hours: Series[float] = pa.Field(alias="hr2d__Roosteruren__c", nullable=True, coerce=True, description="Number of worked hours according to schedule")
    hours: Series[float] = pa.Field(alias="hr2d__Uren__c", nullable=True, coerce=True, description="Number of worked hours in period")
    parttime_start: Series[float] = pa.Field(alias="hr2d__Deeltd_Aanvang__c", nullable=True, coerce=True, description="Part-time factor at start of period")
    parttime_end: Series[float] = pa.Field(alias="hr2d__Deeltd_Einde__c", nullable=True, coerce=True, description="Part-time factor at end of period")
    working_days_fiscal: Series[float] = pa.Field(alias="hr2d__Werkdagen_Fiscaal__c", nullable=True, coerce=True, description="Working days based on fiscal days/year")
    prorata_calendar_days: Series[float] = pa.Field(alias="hr2d__Prorata_KalDg__c", nullable=True, coerce=True, description="Pro-rata factor based on calendar days")
    prorata_working_days: Series[float] = pa.Field(alias="hr2d__Prorata_WrkDg__c", nullable=True, coerce=True, description="Pro-rata factor based on working days")
    prorata_30_days: Series[float] = pa.Field(alias="hr2d__Prorata_30dg__c", nullable=True, coerce=True, description="Pro-rata factor based on 30 days/month")

    # Tax Fields
    wage_tax_credit: Series[float] = pa.Field(alias="hr2d__LH_korting__c", nullable=True, coerce=True, description="Wage tax credit")
    wage_tax_credit_applied: Series[bool] = pa.Field(alias="hr2d__LH_korting_JN__c", nullable=True, coerce=True, description="Wage tax credit applied")
    wage_tax: Series[float] = pa.Field(alias="hr2d__Loonheffing__c", nullable=True, coerce=True, description="Wage tax table")
    wage_tax_special: Series[float] = pa.Field(alias="hr2d__Loonheffing_BT__c", nullable=True, coerce=True, description="Special rate wage tax")
    wage_tax_table: Series[str] = pa.Field(alias="hr2d__Tabel_LH__c", nullable=True, coerce=True, description="Applied wage tax table")
    labor_credit: Series[float] = pa.Field(alias="hr2d__Arbeidskorting__c", nullable=True, coerce=True, description="Calculated labor credit for wage tax")
    wage_tax_base: Series[float] = pa.Field(alias="hr2d__LH_grondslag__c", nullable=True, coerce=True, description="Calculation base for wage tax")
    wage_tax_special_annual: Series[float] = pa.Field(alias="hr2d__LH_BT_jaarln__c", nullable=True, coerce=True, description="Annual wage for special tax rate")
    wage_tax_special_percentage: Series[float] = pa.Field(alias="hr2d__LH_BT_perc__c", nullable=True, coerce=True, description="Special tax rate percentage")
    wage_tax_advantage_rule: Series[bool] = pa.Field(alias="hr2d__LH_voordeelregel__c", nullable=True, coerce=True, description="Advantage rule applied for wage tax")

    # Insurance Fields
    social_security_days: Series[float] = pa.Field(alias="hr2d__SV_dagen__c", nullable=True, coerce=True, description="Number of social security days in period")
    health_insurance_days: Series[float] = pa.Field(alias="hr2d__ZVW_dagen__c", nullable=True, coerce=True, description="Number of health insurance law days in period")
    health_insurance_employer: Series[float] = pa.Field(alias="hr2d__Premie_ZVW_wg__c", nullable=True, coerce=True, description="Employer health insurance contribution")
    health_insurance_employee: Series[float] = pa.Field(alias="hr2d__Premie_ZVW_wn__c", nullable=True, coerce=True, description="Employee health insurance contribution")
    social_security_employer: Series[float] = pa.Field(alias="hr2d__SV_premies_wg__c", nullable=True, coerce=True, description="Total employer social security contributions")
    social_security_employee: Series[float] = pa.Field(alias="hr2d__SV_premies_wn__c", nullable=True, coerce=True, description="Total employee social security contributions")
    wga_wao_employer: Series[float] = pa.Field(alias="hr2d__Premie_WaoWga_wg__c", nullable=True, coerce=True, description="WGA and WAO premium")
    wga_wao_employee: Series[float] = pa.Field(alias="hr2d__Premie_WaoWga_wn__c", nullable=True, coerce=True, description="Employee WGA contribution")
    unemployment_insurance_employer: Series[float] = pa.Field(alias="hr2d__Premie_WW_wg__c", nullable=True, coerce=True, description="Employer unemployment insurance premium")
    unemployment_insurance_employee: Series[float] = pa.Field(alias="hr2d__Premie_WW_wn__c", nullable=True, coerce=True, description="Employee unemployment insurance premium")

    # Leave Fields
    leave_accrual: Series[float] = pa.Field(alias="hr2d__L1_Accrual__c", nullable=True, coerce=True, description="Leave accrual based on worked hours")
    leave_balance: Series[float] = pa.Field(alias="hr2d__L1_Balance__c", nullable=True, coerce=True, description="Leave balance at time of payroll")
    leave_pay_buy: Series[float] = pa.Field(alias="hr2d__L1_PayBuy__c", nullable=True, coerce=True, description="Paid out or bought leave hours")
    leave_capitalization: Series[str] = pa.Field(alias="hr2d__VerlofKapitalisatie__c", nullable=True, coerce=True, description="Leave balances capitalized")

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employee": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "employer": {
                "parent_schema": "EmployerGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "employment_relationship": {
                "parent_schema": "EmploymentRelationshipGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
        add_missing_columns = True  # Add missing columns as nullable
