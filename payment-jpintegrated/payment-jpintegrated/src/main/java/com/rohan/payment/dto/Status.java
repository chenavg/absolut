package com.rohan.payment.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum Status {
    PENDING("Payment is pending processing"),
    PENDING_POSTING("Payment is yet to be posted in the beneficiary account"),
    COMPLETED("Payment has successfully completed"),
    COMPLETED_CREDITED("Status indicating the beneficiary's account has been credited"),
    REJECTED("Payment has been rejected. Please refer to the exception object for error details"),
    RETURNED("Payment has been returned to the debtor party"),
    WAREHOUSED("Payment request was successfully received. The request will be processed in the next available window, typically the next calendar day"),
    BLOCKED("Payment blocked due to sanctions issue");

    private final String description;

    Status(String description) {
        this.description = description;
    }

    @JsonValue
    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return name();
    }

    @JsonCreator
    public static Status fromString(String value) {
        for (Status status : Status.values()) {
            if (status.name().equalsIgnoreCase(value)) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown payment status: " + value);
    }
}
