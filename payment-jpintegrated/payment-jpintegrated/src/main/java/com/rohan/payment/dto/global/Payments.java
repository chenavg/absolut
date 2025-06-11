package com.rohan.payment.dto.global;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Payments {
    private PaymentIdentifiers paymentIdentifiers;
    private String requestedExecutionDate;
    private String transferType;
    private String paymentType;
    private String paymentCurrency;
    private double paymentAmount;

    private Debtor debtor;
    private DebtorAgent debtorAgent;

    private CreditorAgent creditorAgent;
    private Creditor creditor;

    private Purpose purpose;
    private CategoryPurpose categoryPurpose;

    private RemittanceInformation remittanceInformation;
    private TaxInformation taxInformation;

    @Data
    public static class Debtor {
        private String debtorName;
        private DebtorAccount debtorAccount;
        private UltimateDebtor ultimateDebtor;
        private DebtorDevice debtorDevice;
    }

    @Data
    public static class DebtorAccount {
        private String accountId;
        private String accountCurrency;
        private String accountType;
        private String alternateAccountIdentifier;
    }

    @Data
    public static class UltimateDebtor {
        private String ultimateDebtorName;
        private Address postalAddress;
        private String countryOfResidence;
        private OrganizationId organizationId;
        private DateAndPlaceOfBirth dateAndPlaceOfBirth;
        private IndividualId individualId;
    }

    @Data
    public static class DebtorDevice {
        private String ipAddress;
    }

    @Data
    public static class DebtorAgent {
        private FinancialInstitutionId financialInstitutionId;
    }

    @Data
    public static class CreditorAgent {
        private FinancialInstitutionId financialInstitutionId;
    }

    @Data
    public static class FinancialInstitutionId {
        private String bic;
        private ClearingSystemId clearingSystemId;
        private String branchNumber;
    }

    @Data
    public static class ClearingSystemId {
        private String id;
        private String idType;
    }

    @Data
    public static class Creditor {
        private String creditorName;
        private String countryOfResidence;
        private Address postalAddress;
        private CreditorAccount creditorAccount;
        private UltimateCreditor ultimateCreditor;
        private DateAndPlaceOfBirth dateAndPlaceOfBirth;
        private IndividualId individualId;
        private PartyIdentifiers partyIdentifiers;
    }

    @Data
    public static class CreditorAccount {
        private String accountId;
        private String accountType;
        private String alternateAccountIdentifier;
        private String cardExpiryDate;
        private SchemeName schemeName;
    }

    @Data
    public static class UltimateCreditor {
        private String ultimateCreditorName;
        private Address postalAddress;
        private OrganizationId organizationId;
        private DateAndPlaceOfBirth dateAndPlaceOfBirth;
        private IndividualId individualId;
    }

    @Data
    public static class OrganizationId {
        private String id;
        private SchemeName schemeName;
    }

    @Data
    public static class SchemeName {
        private String proprietary;
    }

    @Data
    public static class DateAndPlaceOfBirth {
        private String birthDate;
        private String cityOfBirth;
        private String countryOfBirth;
    }

    @Data
    public static class IndividualId {
        private String id;
        private String issuer;
        private String idType;
    }

    @Data
    public static class PartyIdentifiers {
        private OrganizationId organizationId;
    }

    @Data
    public static class Address {
        private String addressType;
        private String streetName;
        private String buildingNumber;
        private String postalCode;
        private String townName;
        private String country;
        private String countrySubDvsn;
        private List<String> addressLine;
    }

    @Data
    public static class Purpose {
        private String code;
        private String type;
    }

    @Data
    public static class CategoryPurpose {
        private String proprietary;
    }

    @Data
    public static class RemittanceInformation {
        private List<String> unstructuredInformation;
        private List<StructuredInformation> structuredInformation;
    }

    @Data
    public static class StructuredInformation {
        private String creditReference;
    }

    @Data
    public static class TaxInformation {
        private CreditorTaxInformation creditorTaxInformation;
    }

    @Data
    public static class CreditorTaxInformation {
        private String taxId;
        private String taxpayerCategory;
    }
}