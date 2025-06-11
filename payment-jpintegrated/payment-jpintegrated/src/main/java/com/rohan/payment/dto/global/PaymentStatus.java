package com.rohan.payment.dto.global;

import com.rohan.payment.dto.Status;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentStatus{
    PaymentIdentifiers paymentIdentifiers;
    Status status;
    LocalDateTime createDateTime;
}