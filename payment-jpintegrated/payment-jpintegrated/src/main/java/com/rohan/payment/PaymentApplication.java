package com.rohan.payment;

import com.rohan.payment.service.global.GlobalPaymentService;
import com.rohan.payment.service.online.OnlinePaymentService;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbacks;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.List;

@SpringBootApplication
public class PaymentApplication {

    public static void main(String[] args) {
        SpringApplication.run(PaymentApplication.class, args);
    }

    @Bean
    public List<ToolCallback> paymentTools(GlobalPaymentService paymentService, OnlinePaymentService onlinePaymentService) {
        return List.of(ToolCallbacks.from(paymentService, onlinePaymentService));
    }
}