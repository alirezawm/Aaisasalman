package com.asiasalman.mobile.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class LoginUiState(
    val isLoading: Boolean = false,
    val phone: String = "",
    val otpCode: String = "",
    val isOtpSent: Boolean = false,
    val isLoggedIn: Boolean = false,
    val error: String? = null,
    val resendTimer: Int = 0,
    val canResend: Boolean = false
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()
    
    fun updatePhone(phone: String) {
        if (phone.length <= 11 && phone.all { it.isDigit() }) {
            _uiState.value = _uiState.value.copy(phone = phone, error = null)
        }
    }
    
    fun updateOtpCode(code: String) {
        if (code.length <= 6 && code.all { it.isDigit() }) {
            _uiState.value = _uiState.value.copy(otpCode = code, error = null)
        }
    }
    
    fun sendOtp() {
        val phone = _uiState.value.phone
        
        if (!phone.matches(Regex("^09[0-9]{9}$"))) {
            _uiState.value = _uiState.value.copy(error = "شماره موبایل نامعتبر است")
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = repository.sendOtp(phone)) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        isOtpSent = true,
                        resendTimer = 60,
                        canResend = false
                    )
                    startResendTimer()
                }
                is Result.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                is Result.Loading -> { }
            }
        }
    }
    
    fun verifyOtp() {
        val phone = _uiState.value.phone
        val otpCode = _uiState.value.otpCode
        
        if (otpCode.length < 4) {
            _uiState.value = _uiState.value.copy(error = "کد تایید نامعتبر است")
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = repository.verifyOtp(phone, otpCode)) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        isLoggedIn = true
                    )
                }
                is Result.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                is Result.Loading -> { }
            }
        }
    }
    
    fun resetOtp() {
        _uiState.value = _uiState.value.copy(
            isOtpSent = false,
            otpCode = "",
            error = null,
            resendTimer = 0,
            canResend = false
        )
    }
    
    fun setOtpCodeFromSms(code: String) {
        _uiState.value = _uiState.value.copy(otpCode = code, error = null)
    }
    
    private fun startResendTimer() {
        viewModelScope.launch {
            var timeLeft = 60
            while (timeLeft > 0) {
                delay(1000)
                timeLeft--
                _uiState.value = _uiState.value.copy(
                    resendTimer = timeLeft,
                    canResend = false
                )
            }
            _uiState.value = _uiState.value.copy(
                resendTimer = 0,
                canResend = true
            )
        }
    }
}

