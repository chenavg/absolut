package com.rohan.payment.service.global;

import com.rohan.payment.dto.global.PaymentIdentifiers;
import com.rohan.payment.dto.global.PaymentRequest;
import com.rohan.payment.jpmc.client.global.GlobalPaymentClient;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

import java.util.Map;

@Slf4j
@Service
@AllArgsConstructor
public class GlobalPaymentService {

    private GlobalPaymentClient globalPaymentClient;

    @Tool(name = "paymentDetails", description = "Get a payment details")
    public Map<String, Object> paymentDetails(PaymentIdentifiers paymentIdentifiers) {
        Map<String, Object> paymentDetails = globalPaymentClient.getPaymentDetails(paymentIdentifiers);
        log.info("Finding payment for {} ", paymentIdentifiers);
        return paymentDetails;
    }

    @Tool(name = "paymentStatus", description = "Get a payment status")
    public Map<String, Object> paymentStatus(PaymentIdentifiers paymentIdentifiers) {
        Map<String, Object> paymentStatus = globalPaymentClient.getPaymentStatus(paymentIdentifiers);
        log.info("Finding payment status for {} ", paymentIdentifiers);
        return paymentStatus;
    }

    @Tool(name = "initiatePayment", description = "Initiate payments")
    public Map<String, Object> initiatePayment(PaymentRequest paymentRequest) {
        Map<String, Object> paymentDetails = globalPaymentClient.initiatePayment(paymentRequest);
        log.info("Initiating payment for user");
        return paymentDetails;
    }
}