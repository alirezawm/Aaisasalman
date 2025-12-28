package com.asiasalman.autoparts.util

object PhoneNumberValidator {
    fun isValid(phone: String): Boolean {
        val cleaned = phone.replace(Regex("[^0-9]"), "")
        return cleaned.length == 11 && cleaned.startsWith("09")
    }
    
    fun clean(phone: String): String {
        return phone.replace(Regex("[^0-9]"), "")
    }
}

