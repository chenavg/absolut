package com.rohan.payment.jpmc.client.global;

import com.rohan.payment.dto.global.PaymentIdentifiers;
import com.rohan.payment.dto.global.PaymentRequest;
import com.rohan.payment.jpmc.client.JPMAuthService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.Map;

@Service
public class GlobalPaymentClient {
    private final JPMAuthService authService;
    private final RestTemplate restTemplate;
    @Value("${jpmc.api.base-url}")
    private String baseUrl;

    public GlobalPaymentClient(JPMAuthService authService) {
        this.authService = authService;
        this.restTemplate = new RestTemplate();
    }

    public Map<String, Object> initiatePayment(PaymentRequest paymentRequest) {
        String token = authService.getAccessToken();
        String url = baseUrl;

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<PaymentRequest> request = new HttpEntity<>(paymentRequest, headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                request,
                Map.class
        );

        return response.getBody();
    }

    public Map<String, Object> getPaymentDetails(PaymentIdentifiers paymentIdentifiers) {
        String token = authService.getAccessToken();
        String url = baseUrl + "?endToEndId=" + paymentIdentifiers.getEndToEndId() +
                "&firmRootId=" + paymentIdentifiers.getFirmRootId();

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

        HttpEntity<Void> request = new HttpEntity<>(headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class
        );

        return response.getBody();
    }

    public Map<String, Object> getPaymentStatus(PaymentIdentifiers paymentIdentifiers) {
        String token = authService.getAccessToken();
        String url = baseUrl + "/status?endToEndId=" + paymentIdentifiers.getEndToEndId() +
                "&firmRootId=" + paymentIdentifiers.getFirmRootId();

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

        HttpEntity<Void> request = new HttpEntity<>(headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class
        );
        return response.getBody();
    }
}