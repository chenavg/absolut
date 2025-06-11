package com.rohan.payment.jpmc.client.online;

import com.rohan.payment.dto.online.OnlinePaymentRequest;
import com.rohan.payment.jpmc.client.JPMAuthService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.Map;

@Service
public class OnlinePaymentClient {
    private final JPMAuthService authService;
    private final RestTemplate restTemplate;
    @Value("${jpmc.openpay.api.base-url}")
    private String baseUrl;

    public OnlinePaymentClient(JPMAuthService authService) {
        this.authService = authService;
        this.restTemplate = new RestTemplate();
    }

    public Map<String, Object> transactionByTransactionId(String merchantId, String transactionId) {
        String token = authService.getAccessToken();
        String url = baseUrl + "/" + transactionId;

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));
        headers.add("merchant-id", merchantId);
        HttpEntity<Void> request = new HttpEntity<>(headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class
        );
        return response.getBody();
    }

    public Map<String, Object> transactionByRequestId(String requestIdentifier, String merchantId, String requestId) {
        String token = authService.getAccessToken();
        String url = baseUrl + "?requestIdentifier=" + requestIdentifier;

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));
        headers.add("merchant-id", merchantId);
        headers.add("request-id", requestId);
        HttpEntity<Void> request = new HttpEntity<>(headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class
        );
        return response.getBody();
    }

    public Map<String, Object> initiatePayment(OnlinePaymentRequest paymentRequest, String merchantID, String requestId) {
        String token = authService.getAccessToken();
        String url = baseUrl;
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.add("merchant-id", merchantID);
        headers.add("request-id", requestId);
        HttpEntity<OnlinePaymentRequest> request = new HttpEntity<>(paymentRequest, headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                request,
                Map.class
        );
        return response.getBody();
    }

    public Map<String, Object> paymentByRequestId(String requestIdentifier, String merchantId, String merchantIdentifier) {
        return null;
    }

    public Map<String, Object> paymentByTransactionId(String merchantId, String transactionId) {
        return null;
    }
}