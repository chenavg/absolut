package com.rohan.payment.jpmc.client;

import com.rohan.payment.dto.AccountRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class ValidationClient {
    @Value("${jpmc.validation.api.base-url}")
    private String baseUrl;

    private final JPMAuthService authService;
    private final RestTemplate restTemplate;

    public ValidationClient(JPMAuthService authService) {
        this.authService = authService;
        this.restTemplate = new RestTemplate();
    }

    /*************
     * curl --request POST \
     *   --url https://api-mock.payments.jpmorgan.com/tsapi/v2/validations/accounts \
     *   --header 'Accept: application/json' \
     *   --header 'Content-Type: application/json' \
     *   --header 'x-client-id: CLIENTID' \
     *   --header 'x-program-id: VERIAUTH' \
     *   --header 'x-program-id-type: AVS' \

     * @param accountRequest
     * @return
     */
    public Map<String, Object> validateAccount(AccountRequest accountRequest) {
        String token = authService.getAccessToken();
        String url = baseUrl;
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        headers.setContentType(MediaType.APPLICATION_JSON);
//        headers.add("merchant-id", merchantID);
//        headers.add("request-id", requestId);
        HttpEntity<AccountRequest> request = new HttpEntity<>(accountRequest, headers);

        ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                request,
                Map.class
        );

        return response.getBody();
    }

}
