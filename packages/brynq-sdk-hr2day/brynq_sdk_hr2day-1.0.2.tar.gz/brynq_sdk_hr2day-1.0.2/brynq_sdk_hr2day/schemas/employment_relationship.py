from typing import Optional
from datetime import date, datetime
from pandera.typing import Series
import pandera as pa

from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmploymentRelationshipGet(BrynQPanderaDataFrameModel):
    """Schema for hr2d__Arbeidsrelatie__c entity in HR2Day. Represents an employment relationship record."""

    # Salesforce Standard Fields
    id: Series[str] = pa.Field(alias="Id", nullable=False, coerce=True, description="Record ID")
    is_deleted: Series[bool] = pa.Field(alias="IsDeleted", nullable=True, coerce=True, description="Is Deleted")
    name: Series[str] = pa.Field(alias="Name", nullable=False, coerce=True, description="Employment")
    created_by_id: Series[str] = pa.Field(alias="CreatedById", nullable=True, coerce=True, description="Created By ID")
    created_date: Series[datetime] = pa.Field(alias="CreatedDate", nullable=True, coerce=True, description="Created Date")
    last_activity_date: Optional[Series[datetime]] = pa.Field(alias="LastActivityDate", nullable=True, coerce=True, description="Last Activity Date")
    last_modified_by_id: Series[str] = pa.Field(alias="LastModifiedById", nullable=True, coerce=True, description="Last Modified By ID")
    last_modified_date: Series[datetime] = pa.Field(alias="LastModifiedDate", nullable=True, coerce=True, description="Last Modified Date")
    system_modstamp: Series[datetime] = pa.Field(alias="SystemModstamp", nullable=True, coerce=True, description="System Modstamp")

    # HR2Day Custom Fields - Employment Details
    start_date: Optional[Series[date]] = pa.Field(alias="hr2d__Aanvang_arbrel__c", nullable=True, coerce=True, description="Start date of employment")
    employment_type: Optional[Series[str]] = pa.Field(alias="hr2d__Aard_arbverh__c", nullable=True, coerce=True, description="Kind of employment")
    employment_conditions_cluster: Optional[Series[str]] = pa.Field(alias="hr2d__ArbVoorwCluster__c", nullable=True, coerce=True, description="Employment conditions group")
    end_date: Optional[Series[date]] = pa.Field(alias="hr2d__Einde_arbrel__c", nullable=True, coerce=True, description="End date of employment")
    end_date_filter: Optional[Series[str]] = pa.Field(alias="hr2d__Einde_arbrelFilter__c", nullable=True, coerce=True, description="End date of employment (filter field)")
    employee: Optional[Series[str]] = pa.Field(alias="hr2d__Employee__c", nullable=True, coerce=True, description="Employee")
    employment_number: Optional[Series[float]] = pa.Field(alias="hr2d__Volgnummer__c", nullable=True, coerce=True, description="Employment number")
    employment_type_description: Optional[Series[str]] = pa.Field(alias="hr2d__TypeArbrel__c", nullable=True, coerce=True, description="Type of employment")

    # Contract Details
    contract_start_date: Optional[Series[date]] = pa.Field(alias="hr2d__Contract_Aanvang__c", nullable=True, coerce=True, description="Contract start date")
    contract_end_date: Optional[Series[date]] = pa.Field(alias="hr2d__Contract_Einde__c", nullable=True, coerce=True, description="Contract end date")
    contract_termination_date: Optional[Series[date]] = pa.Field(alias="hr2d__Contract_Opzegdatum__c", nullable=True, coerce=True, description="Contract termination date")
    contract_sequence_number: Optional[Series[float]] = pa.Field(alias="hr2d__Contract_Volgnr__c", nullable=True, coerce=True, description="Contract sequence number")
    contract_temporary: Optional[Series[str]] = pa.Field(alias="hr2d__Contract_bep_tijd__c", nullable=True, coerce=True, description="Contract temporary/unlimited")
    written_employment_agreement: Optional[Series[str]] = pa.Field(alias="hr2d__SchriftArbOvk__c", nullable=True, coerce=True, description="Written employment agreement")
    probation_end_date: Optional[Series[date]] = pa.Field(alias="hr2d__Proeftijd_einde__c", nullable=True, coerce=True, description="Probation period end")
    reason_end_employment: Optional[Series[str]] = pa.Field(alias="hr2d__RedenEindeArbrel__c", nullable=True, coerce=True, description="Reason end of employment")

    # Department and Cost Center
    department: Optional[Series[str]] = pa.Field(alias="hr2d__Department__c", nullable=True, coerce=True, description="Department")
    department_2: Optional[Series[str]] = pa.Field(alias="hr2d__Department_2__c", nullable=True, coerce=True, description="Department 2")
    department_3: Optional[Series[str]] = pa.Field(alias="hr2d__Department_3__c", nullable=True, coerce=True, description="Department 3")
    cost_center: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter__c", nullable=True, coerce=True, description="Cost center")
    cost_center_2: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_2__c", nullable=True, coerce=True, description="Cost center 2")
    cost_center_3: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_3__c", nullable=True, coerce=True, description="Cost center 3")
    cost_center_dim2: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim2__c", nullable=True, coerce=True, description="Cost center Dim2")
    cost_center_dim2_2: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim2_2__c", nullable=True, coerce=True, description="Cost center Dim2 - 2")
    cost_center_dim2_3: Optional[Series[str]] = pa.Field(alias="hr2d__CostCenter_Dim2_3__c", nullable=True, coerce=True, description="Cost center Dim2 - 3")
    alternate_cost_center: Optional[Series[bool]] = pa.Field(alias="hr2d__CostCenterAfw__c", nullable=True, coerce=True, description="Alternate cost center")

    # Job and Function
    job: Optional[Series[str]] = pa.Field(alias="hr2d__Job__c", nullable=True, coerce=True, description="Job")
    job_2: Optional[Series[str]] = pa.Field(alias="hr2d__Job_2__c", nullable=True, coerce=True, description="Job 2")
    job_3: Optional[Series[str]] = pa.Field(alias="hr2d__Job_3__c", nullable=True, coerce=True, description="Job 3")
    function: Optional[Series[str]] = pa.Field(alias="hr2d__Functie__c", nullable=True, coerce=True, description="Job title")
    function_2: Optional[Series[str]] = pa.Field(alias="hr2d__Functie_2__c", nullable=True, coerce=True, description="Job title 2")
    function_3: Optional[Series[str]] = pa.Field(alias="hr2d__Functie_3__c", nullable=True, coerce=True, description="Job title 3")

    # Working Hours and Part-time
    hours_per_week: Optional[Series[float]] = pa.Field(alias="hr2d__UrenWeek__c", nullable=True, coerce=True, description="Hours per week")
    part_time_factor: Optional[Series[float]] = pa.Field(alias="hr2d__DeeltijdFactor__c", nullable=True, coerce=True, description="Part-time factor")
    part_time_factor_total: Optional[Series[float]] = pa.Field(alias="hr2d__DeeltijdFactorTotaal__c", nullable=True, coerce=True, description="Part-time factor total")
    part_time_factor_variable: Optional[Series[float]] = pa.Field(alias="hr2d__DeeltijdFactorVar__c", nullable=True, coerce=True, description="Part-time factor variable")
    part_time_percentage: Optional[Series[float]] = pa.Field(alias="hr2d__DeeltijdPerc__c", nullable=True, coerce=True, description="Part-time percentage")

    # Salary and Pay Scale
    salary: Optional[Series[float]] = pa.Field(alias="hr2d__Salaris__c", nullable=True, coerce=True, description="Salary")
    fulltime_salary: Optional[Series[float]] = pa.Field(alias="hr2d__Fulltime_Salaris__c", nullable=True, coerce=True, description="Fulltime salary")
    hourly_wage: Optional[Series[float]] = pa.Field(alias="hr2d__Uurloon__c", nullable=True, coerce=True, description="Hourly wage")
    hourly_wage_2: Optional[Series[float]] = pa.Field(alias="hr2d__Uurloon2__c", nullable=True, coerce=True, description="Hourly wage 2")
    hourly_wage_3: Optional[Series[float]] = pa.Field(alias="hr2d__Uurloon3__c", nullable=True, coerce=True, description="Hourly wage 3")
    pay_scale: Optional[Series[str]] = pa.Field(alias="hr2d__Schaal__c", nullable=True, coerce=True, description="Pay scale")
    pay_scale_level: Optional[Series[str]] = pa.Field(alias="hr2d__Trede__c", nullable=True, coerce=True, description="Pay scale level")
    guaranteed_pay_scale: Optional[Series[str]] = pa.Field(alias="hr2d__Garantieschaal__c", nullable=True, coerce=True, description="Guaranteed pay scale")
    guaranteed_pay_scale_level: Optional[Series[str]] = pa.Field(alias="hr2d__Garantietrede__c", nullable=True, coerce=True, description="Guaranteed pay scale level")
    alternate_salary: Optional[Series[bool]] = pa.Field(alias="hr2d__Salaris_Afwijkend__c", nullable=True, coerce=True, description="Alternate salary")
    relative_salary_position: Optional[Series[float]] = pa.Field(alias="hr2d__RSP__c", nullable=True, coerce=True, description="Relative Salary Position")

    # Validity Period
    valid_from: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_van__c", nullable=True, coerce=True, description="Valid from")
    valid_until: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_tot__c", nullable=True, coerce=True, description="Valid until")
    valid_until_filter: Optional[Series[str]] = pa.Field(alias="hr2d__Geldig_totFilter__c", nullable=True, coerce=True, description="Valid until (filter field)")
    valid_from_in_context: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_vanInContext__c", nullable=True, coerce=True, description="Valid from (in context start/end empl)")
    valid_until_in_context: Optional[Series[date]] = pa.Field(alias="hr2d__Geldig_totInContext__c", nullable=True, coerce=True, description="Valid until (in context start/end empl)")

    # Additional Fields
    cao_code: Optional[Series[str]] = pa.Field(alias="hr2d__CAO_code__c", nullable=True, coerce=True, description="CAO code")
    cao_indication: Optional[Series[str]] = pa.Field(alias="hr2d__CAO_kenmerk__c", nullable=True, coerce=True, description="CAO indication")
    company: Optional[Series[str]] = pa.Field(alias="hr2d__Company__c", nullable=True, coerce=True, description="Company")
    contact_person: Optional[Series[str]] = pa.Field(alias="hr2d__ContactPerson__c", nullable=True, coerce=True, description="Contact person")
    details: Optional[Series[str]] = pa.Field(alias="hr2d__Bijzonderheden__c", nullable=True, coerce=True, description="Details")
    activities: Optional[Series[str]] = pa.Field(alias="hr2d__Werkzaamheden__c", nullable=True, coerce=True, description="Activities")
    notes: Optional[Series[str]] = pa.Field(alias="hr2d__Notes__c", nullable=True, coerce=True, description="Notes")
    key: Optional[Series[str]] = pa.Field(alias="hr2d__Key__c", nullable=True, coerce=True, description="Key")

    # Car Fields
    car: Optional[Series[str]] = pa.Field(alias="hr2d__Auto__c", nullable=True, coerce=True, description="Car")
    car_contribution_add: Optional[Series[float]] = pa.Field(alias="hr2d__AutoBijdrage__c", nullable=True, coerce=True, description="Car contribution add. (non deductable)")
    car_contribution_private: Optional[Series[float]] = pa.Field(alias="hr2d__AutoBijdragePrive__c", nullable=True, coerce=True, description="Car contribution (deductable)")
    car_date: Optional[Series[date]] = pa.Field(alias="hr2d__AutoDatum__c", nullable=True, coerce=True, description="Car date of first registration")
    car_license_plate: Optional[Series[str]] = pa.Field(alias="hr2d__AutoKenteken__c", nullable=True, coerce=True, description="Car license plate")
    car_make_type: Optional[Series[str]] = pa.Field(alias="hr2d__AutoMerkType__c", nullable=True, coerce=True, description="Car make/type")
    car_reason_no_addition: Optional[Series[str]] = pa.Field(alias="hr2d__AutoRdnGnBijt__c", nullable=True, coerce=True, description="Car reason no addition")
    car_typing: Optional[Series[str]] = pa.Field(alias="hr2d__AutoTypering__c", nullable=True, coerce=True, description="Car type")
    car_value: Optional[Series[float]] = pa.Field(alias="hr2d__AutoWaarde__c", nullable=True, coerce=True, description="Car value")

    # Bank Fields
    bank_2: Optional[Series[str]] = pa.Field(alias="hr2d__Bank2__c", nullable=True, coerce=True, description="Bank account 2")
    bank_2_amount: Optional[Series[float]] = pa.Field(alias="hr2d__Bank2_Bedrag__c", nullable=True, coerce=True, description="Bank 2 Amount")
    bank_2_iban: Optional[Series[str]] = pa.Field(alias="hr2d__Bank2_IBAN__c", nullable=True, coerce=True, description="Bank 2 IBAN")
    bank_2_holder_name: Optional[Series[str]] = pa.Field(alias="hr2d__Bank2_naam__c", nullable=True, coerce=True, description="Bank 2 holder name")
    bank_2_description: Optional[Series[str]] = pa.Field(alias="hr2d__Bank2_omschr__c", nullable=True, coerce=True, description="Bank 2 description")
    bank_2_percentage: Optional[Series[float]] = pa.Field(alias="hr2d__Bank2_Perc__c", nullable=True, coerce=True, description="Bank 2 percentage")

    # Blocking Fields
    block: Optional[Series[str]] = pa.Field(alias="hr2d__Blokkeren__c", nullable=True, coerce=True, description="Block")
    block_increases: Optional[Series[str]] = pa.Field(alias="hr2d__BlokVerhoging__c", nullable=True, coerce=True, description="Block increases")

    # End of Year Regulations
    end_year_regulation_1: Optional[Series[str]] = pa.Field(alias="hr2d__Eindjr1__c", nullable=True, coerce=True, description="End-of-year regulation 1")
    end_year_regulation_2: Optional[Series[str]] = pa.Field(alias="hr2d__Eindjr2__c", nullable=True, coerce=True, description="End-of-year regulation 2")
    end_year_regulation_3: Optional[Series[str]] = pa.Field(alias="hr2d__Eindjr3__c", nullable=True, coerce=True, description="End-of-year regulation 3")
    end_year_regulation_4: Optional[Series[str]] = pa.Field(alias="hr2d__Eindjr4__c", nullable=True, coerce=True, description="End-of-year regulation 4")
    end_year_regulation_5: Optional[Series[str]] = pa.Field(alias="hr2d__Eindjr5__c", nullable=True, coerce=True, description="End-of-year regulation 5")

    # Bicycle Fields
    bicycle: Optional[Series[str]] = pa.Field(alias="hr2d__Fiets__c", nullable=True, coerce=True, description="Bicycle")
    bicycle_contribution: Optional[Series[float]] = pa.Field(alias="hr2d__FietsBijdrage__c", nullable=True, coerce=True, description="Bicycle contribution")
    bicycle_value: Optional[Series[float]] = pa.Field(alias="hr2d__FietsWaarde__c", nullable=True, coerce=True, description="Bicycle value")

    # Fiscal Fields
    fiscal_rule: Optional[Series[str]] = pa.Field(alias="hr2d__FiscReg__c", nullable=True, coerce=True, description="Fiscal rule")
    tax_reduction_education: Optional[Series[str]] = pa.Field(alias="hr2d__Av_Onderwijs__c", nullable=True, coerce=True, description="Tax reduction Education")

    # Location Fields
    location: Optional[Series[str]] = pa.Field(alias="hr2d__Location__c", nullable=True, coerce=True, description="Location")
    location_monday: Optional[Series[str]] = pa.Field(alias="hr2d__Location01__c", nullable=True, coerce=True, description="Location Monday")
    location_tuesday: Optional[Series[str]] = pa.Field(alias="hr2d__Location02__c", nullable=True, coerce=True, description="Location Tuesday")
    location_wednesday: Optional[Series[str]] = pa.Field(alias="hr2d__Location03__c", nullable=True, coerce=True, description="Location Wednesday")
    location_thursday: Optional[Series[str]] = pa.Field(alias="hr2d__Location04__c", nullable=True, coerce=True, description="Location Thursday")
    location_friday: Optional[Series[str]] = pa.Field(alias="hr2d__Location05__c", nullable=True, coerce=True, description="Location Friday")
    location_saturday: Optional[Series[str]] = pa.Field(alias="hr2d__Location06__c", nullable=True, coerce=True, description="Location Saturday")
    location_sunday: Optional[Series[str]] = pa.Field(alias="hr2d__Location07__c", nullable=True, coerce=True, description="Location Sunday")

    # Wage Garnishment Fields
    wage_garnishment_bank: Optional[Series[str]] = pa.Field(alias="hr2d__Loonbeslag_Bank__c", nullable=True, coerce=True, description="Bank wage garnishment")
    wage_garnishment_bank_iban: Optional[Series[str]] = pa.Field(alias="hr2d__Loonbeslag_Bank_IBAN__c", nullable=True, coerce=True, description="Bank wage garnishment IBAN")
    wage_garnishment_bank_holder_name: Optional[Series[str]] = pa.Field(alias="hr2d__Loonbeslag_Bank_naam__c", nullable=True, coerce=True, description="Bank wage garnishment holder name")
    wage_garnishment_bank_description: Optional[Series[str]] = pa.Field(alias="hr2d__Loonbeslag_Bank_omschr__c", nullable=True, coerce=True, description="Bank wage garnishment description")
    wage_garnishment_number: Optional[Series[str]] = pa.Field(alias="hr2d__Loonbeslag_Nr__c", nullable=True, coerce=True, description="Wage garnishment sequence nr/ id")
    wage_garnishment_period_amount: Optional[Series[float]] = pa.Field(alias="hr2d__Loonbeslag_Periode__c", nullable=True, coerce=True, description="Wage garnishment period amount")
    wage_garnishment_total_amount: Optional[Series[float]] = pa.Field(alias="hr2d__Loonbeslag_Totaal__c", nullable=True, coerce=True, description="Wage garnishment total amount")
    wage_garnishment_exempt_amount: Optional[Series[float]] = pa.Field(alias="hr2d__Loonbeslag_Vrij__c", nullable=True, coerce=True, description="Wage garnishment exempt amount")

    # Pension Fields
    pension_1: Optional[Series[str]] = pa.Field(alias="hr2d__Pensioen1__c", nullable=True, coerce=True, description="Participate Pension 1")
    pension_1_start_date: Optional[Series[date]] = pa.Field(alias="hr2d__Pensioen1_Aanvang__c", nullable=True, coerce=True, description="Pension 1 Start date")
    pension_1_end_date: Optional[Series[date]] = pa.Field(alias="hr2d__Pensioen1_Einde__c", nullable=True, coerce=True, description="Pension 1 End date")
    pension_1_base_additional: Optional[Series[float]] = pa.Field(alias="hr2d__Pensioen1_Grsl_Add__c", nullable=True, coerce=True, description="Pension base additional")
    pension_1_base_fixed: Optional[Series[float]] = pa.Field(alias="hr2d__Pensioen1_Grsl_Vast__c", nullable=True, coerce=True, description="Pension base fixed")
    pension_1_policy_number: Optional[Series[str]] = pa.Field(alias="hr2d__Pensioen1_Polisnr__c", nullable=True, coerce=True, description="Pension policy number")

    # Regulations
    regulation_1: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling1__c", nullable=True, coerce=True, description="Regulation 1")
    regulation_2: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling2__c", nullable=True, coerce=True, description="Regulation 2")
    regulation_3: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling3__c", nullable=True, coerce=True, description="Regulation 3")
    regulation_4: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling4__c", nullable=True, coerce=True, description="Regulation 4")
    regulation_5: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling5__c", nullable=True, coerce=True, description="Regulation 5")
    regulation_30_percent: Optional[Series[str]] = pa.Field(alias="hr2d__Regeling30P__c", nullable=True, coerce=True, description="30% Ruling")
    regulation_30_percent_end_date: Optional[Series[date]] = pa.Field(alias="hr2d__Regeling30P_Einddat__c", nullable=True, coerce=True, description="30% Ruling End date")

    # Travel Cost Fields
    travel_cost_notes: Optional[Series[str]] = pa.Field(alias="hr2d__Reiskn_Notities__c", nullable=True, coerce=True, description="Travel cost notes")
    travel_cost_balancing: Optional[Series[str]] = pa.Field(alias="hr2d__Reiskn_Saldering__c", nullable=True, coerce=True, description="Travel costs balancing")
    travel_allowance: Optional[Series[float]] = pa.Field(alias="hr2d__Reiskn_Verg__c", nullable=True, coerce=True, description="Travel allowance")
    travel_allowance_regulation: Optional[Series[str]] = pa.Field(alias="hr2d__Reiskn_Verg_Regeling__c", nullable=True, coerce=True, description="Travel allowance regulation")
    travel_allowance_settlement: Optional[Series[str]] = pa.Field(alias="hr2d__Reiskn_Verrekening__c", nullable=True, coerce=True, description="Travel allowance settlement")

    # Schedule Fields
    schedule: Optional[Series[str]] = pa.Field(alias="hr2d__Rooster__c", nullable=True, coerce=True, description="Shift")
    schedule_days_per_week: Optional[Series[float]] = pa.Field(alias="hr2d__Rooster_DagenWk__c", nullable=True, coerce=True, description="Shift days/week")

    # Insurance Fields
    wao_wia_insured: Optional[Series[bool]] = pa.Field(alias="hr2d__WaoWia__c", nullable=True, coerce=True, description="Insured for WAO/WIA")
    ww_insured: Optional[Series[bool]] = pa.Field(alias="hr2d__WW__c", nullable=True, coerce=True, description="Insured for WW/WG/Ufo")
    ww_alternate_situation: Optional[Series[str]] = pa.Field(alias="hr2d__WW_afwijkend__c", nullable=True, coerce=True, description="WW alternate situation (WAB)")
    zw_insured: Optional[Series[str]] = pa.Field(alias="hr2d__ZVW__c", nullable=True, coerce=True, description="Insured for ZVW")
    zw_nominal: Optional[Series[float]] = pa.Field(alias="hr2d__ZVW_Nominaal__c", nullable=True, coerce=True, description="ZVW nominal")
    zw_country_of_residence: Optional[Series[str]] = pa.Field(alias="hr2d__ZVW_Woonland__c", nullable=True, coerce=True, description="Country of residence")
    zw_insured_zw: Optional[Series[bool]] = pa.Field(alias="hr2d__ZW__c", nullable=True, coerce=True, description="Insured for ZW")

    # Commuter Traffic Fields
    commuter_traffic_regulation: Optional[Series[str]] = pa.Field(alias="hr2d__WoonWerk__c", nullable=True, coerce=True, description="Commuter traffic regulation")
    commuter_traffic_days: Optional[Series[float]] = pa.Field(alias="hr2d__WoonWerk_Dagen__c", nullable=True, coerce=True, description="Days commuter traffic")
    commuter_traffic_details: Optional[Series[str]] = pa.Field(alias="hr2d__WoonWerk_Details__c", nullable=True, coerce=True, description="Commuter traffic details")
    commuter_traffic_km: Optional[Series[float]] = pa.Field(alias="hr2d__WoonWerk_KM__c", nullable=True, coerce=True, description="KM home-work")
    commuter_traffic_km_schedule: Optional[Series[str]] = pa.Field(alias="hr2d__WoonWerk_KM_Rooster__c", nullable=True, coerce=True, description="KM home-work shift")
    commuter_traffic_allowance: Optional[Series[float]] = pa.Field(alias="hr2d__WoonWerk_Verg__c", nullable=True, coerce=True, description="Commuter traffic allowance")

    # Other Important Fields
    uninterrupted_employed_since: Optional[Series[date]] = pa.Field(alias="hr2d__OnonderbrokenInDienst__c", nullable=True, coerce=True, description="Uninterrupted employed since")
    on_call_agreement: Optional[Series[str]] = pa.Field(alias="hr2d__OproepOvk__c", nullable=True, coerce=True, description="On-call agreement")
    agreement_pc: Optional[Series[bool]] = pa.Field(alias="hr2d__Ovk_PC__c", nullable=True, coerce=True, description="Agreement PC")
    agreement_phone: Optional[Series[bool]] = pa.Field(alias="hr2d__Ovk_Telefoon__c", nullable=True, coerce=True, description="Agreement Phone")
    alternate_final_settlement: Optional[Series[str]] = pa.Field(alias="hr2d__Eindafrek__c", nullable=True, coerce=True, description="Alternate final settlement calculation")
    alternate_leave_regulation: Optional[Series[str]] = pa.Field(alias="hr2d__VerlofregelingAfw__c", nullable=True, coerce=True, description="Alternate Leaveregulation")
    payroll_processing_until: Optional[Series[date]] = pa.Field(alias="hr2d__Verlonen_tot__c", nullable=True, coerce=True, description="Payroll processing until")
    means_of_transport: Optional[Series[str]] = pa.Field(alias="hr2d__Vervoermiddel__c", nullable=True, coerce=True, description="Means of transport")
    previous_employment_id: Optional[Series[str]] = pa.Field(alias="hr2d__Vrg_Arbrel_ID__c", nullable=True, coerce=True, description="Previous Employment (ID)")
    changes: Optional[Series[str]] = pa.Field(alias="hr2d__Wijzigingen__c", nullable=True, coerce=True, description="Changes")
    change_date_variable: Optional[Series[datetime]] = pa.Field(alias="hr2d__WijzigdatumVar__c", nullable=True, coerce=True, description="Changedate variable data")
    change_date_variable_start: Optional[Series[date]] = pa.Field(alias="hr2d__WijzigdatumVarGeldig_van__c", nullable=True, coerce=True, description="Changedate variable data start date")
    change_date_fixed: Optional[Series[datetime]] = pa.Field(alias="hr2d__WijzigdatumVast__c", nullable=True, coerce=True, description="Changedate fixed data")

    class _Annotation:
        """Annotation class for primary and foreign keys"""
        primary_key = "id"
        foreign_keys = {
            "employee": {
                "parent_schema": "EmployeeGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "department": {
                "parent_schema": "DepartmentGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "cost_center": {
                "parent_schema": "CostCenterGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "job": {
                "parent_schema": "JobGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "employment_conditions_cluster": {
                "parent_schema": "EmploymentConditionsClusterGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

    class Config:
        """Schema configuration"""
        strict = "filter"  # Allow extra columns not defined in schema
        coerce = True
