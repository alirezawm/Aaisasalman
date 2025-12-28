package com.asiasalman.autoparts.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.AuthResponse
import com.asiasalman.autoparts.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OTPVerificationViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _verificationSuccess = MutableLiveData<AuthResponse?>()
    val verificationSuccess: LiveData<AuthResponse?> = _verificationSuccess
    
    private val _otpResent = MutableLiveData<Boolean>()
    val otpResent: LiveData<Boolean> = _otpResent
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun verifyOTP(phone: String, otpCode: String) {
        viewModelScope.launch {
            _loading.value = true
            _error.value = null
            
            authRepository.verifyOTP(phone, otpCode).fold(
                onSuccess = {
                    _verificationSuccess.value = it
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "کد تایید معتبر نیست"
                    _loading.value = false
                }
            )
        }
    }
    
    fun resendOTP(phone: String) {
        viewModelScope.launch {
            authRepository.sendOTP(phone).fold(
                onSuccess = {
                    _otpResent.value = true
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "خطا در ارسال مجدد کد"
                }
            )
        }
    }
}

