package com.rohan.payment.dto.global;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PaymentRequest {
    private Payments payments;

    @Data
    public static class Payments {
        private boolean possibleDuplicateMessage=false;
        private PaymentIdentifiers paymentIdentifiers;
        private String requestedExecutionDate = DateTimeFormatter.ofPattern("yyyy-MM-dd").format(LocalDate.now());
        private String transferType="RTP";
        private String paymentCurrency;
        private int paymentAmount;
        private String paymentType;
        private Debtor debtor;
        private DebtorAgent debtorAgent;
        private CreditorAgent creditorAgent;
        private Creditor creditor;
        private Purpose purpose;
        private RemittanceInformation remittanceInformation;
    }

    @Data
    public static class PaymentIdentifiers {
        private String endToEndId;
    }

    @Data
    public static class Debtor {
        private DebtorAccount debtorAccount;
//        private UltimateDebtor ultimateDebtor;
    }

    @Data
    public static class DebtorAccount {
        private String accountId;
        private String accountCurrency;
        private String accountType;
    }

    @Data
    public static class UltimateDebtor {
        private String ultimateDebtorName;
        private PostalAddress postalAddress;
        private String countryOfResidence;
        private OrganizationId organizationId;
    }

    @Data
    public static class OrganizationId {
        private String bic;
        private String id;
    }

    @Data
    public static class PostalAddress {
        private String addressType="Home";
        private String streetName="";
        private String buildingNumber="";
        private String postalCode;
        private String townName;
        private String country;
        private String countrySubDvsn="";
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
    }

    @Data
    public static class ClearingSystemId {
        private String id;
    }

    @Data
    public static class Creditor {
        private String creditorName;
        private PostalAddress postalAddress;
        private String countryOfResidence;
        private CreditorAccount creditorAccount;
        private UltimateCreditor ultimateCreditor;
    }

    @Data
    public static class CreditorAccount {
        private String accountId;
    }

    @Data
    public static class UltimateCreditor {
        private String ultimateCreditorName;
        private IndividualId individualId;
        private PostalAddress postalAddress;
    }

    @Data
    public static class IndividualId {
        private String id;
    }

    @Data
    public static class Purpose {
        private String code;
        private String type = "CODE";
    }

    @Data
    public static class RemittanceInformation {
        private List<String> unstructuredInformation;
    }
}