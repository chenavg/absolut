package com.rohan.payment.dto;

import lombok.Data;

@Data
public class AccountRequest {
    private String requestId;
    private Account account;
    private Entity entity;

    @Data
    public static class Account {
        private String accountNumber;
        private FinancialInstitutionId financialInstitutionId;
    }

    @Data
    public static class FinancialInstitutionId {
        private ClearingSystemId clearingSystemId;
    }

    @Data
    public static class ClearingSystemId {
        private String id;
        private String idType;
    }

    @Data
    public static class Entity {
        private Individual individual;
    }

    @Data
    public static class Individual {
        private String firstName;
        private String lastName;
        private String fullName;
    }
}
