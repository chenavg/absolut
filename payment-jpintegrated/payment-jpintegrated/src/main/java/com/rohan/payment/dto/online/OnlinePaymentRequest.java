package com.rohan.payment.dto.online;


import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class OnlinePaymentRequest {
    private String captureMethod="NOW";
    private int amount;
    private String currency;
    private Merchant merchant;
    private PaymentMethodType paymentMethodType;
    private String initiatorType="CARDHOLDER";
    private String accountOnFile;
    private boolean isAmountFinal;

    @Data
    public static class Merchant {
        private MerchantSoftware merchantSoftware;
        private String merchantCategoryCode;
    }

    @Data
    public static class MerchantSoftware {
        private String companyName;
        private String productName;
        private String version= String.valueOf(0);
    }

    @Data
    public static class PaymentMethodType {
        private Card card;
    }

    @Data
    public static class Card {
        private String accountNumber;
        private Expiry expiry;
        private boolean isBillPayment=true;
    }

    @Data
    public static class Expiry {
        private int month;
        private int year;
    }
}
