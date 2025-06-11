package com.rohan.payment.service.online;

import com.rohan.payment.dto.online.OnlinePaymentRequest;
import com.rohan.payment.jpmc.client.online.OnlinePaymentClient;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@AllArgsConstructor
public class OnlinePaymentService {

    private OnlinePaymentClient onlinePaymentClient;

    @Tool(name = "transactionByRequestId", description = "Get a transaction details by request id for online payments")
    public Map<String, Object> transactionByRequestId(String merchantId, String requestId) {
        String requestIdentifier = UUID.randomUUID().toString();
        Map<String, Object> transactionDetails = onlinePaymentClient.transactionByRequestId(requestIdentifier, merchantId, requestId);
        log.info("Finding payment for [{} - {} - {}] ", requestIdentifier, merchantId, requestId);
        return transactionDetails;
    }

    @Tool(name = "transactionByTransactionId", description = "Get a transaction details by Transaction id for online payments")
    public Map<String, Object> transactionByTransactionId(String merchantId, String transactionId) {
        Map<String, Object> transactionDetails = onlinePaymentClient.transactionByTransactionId(merchantId, transactionId);
        log.info("Finding payment for [{} - {}] ", merchantId, transactionId);
        return transactionDetails;
    }

    @Tool(name = "initiateOnlinePayment", description = "Initiate payment for online payments")
    public Map<String, Object> initiatePayment(OnlinePaymentRequest paymentRequest) {
        String requestId = UUID.randomUUID().toString();
        Map<String, Object> paymentDetails = onlinePaymentClient.initiatePayment(paymentRequest, "998482157630", requestId);
        log.info("Initiating online payment for user");
        return paymentDetails;
    }
}