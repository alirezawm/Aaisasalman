package com.asiasalman.autoparts.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _otpSent = MutableLiveData<Boolean>()
    val otpSent: LiveData<Boolean> = _otpSent
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun sendOTP(phone: String) {
        viewModelScope.launch {
            _loading.value = true
            _error.value = null
            
            authRepository.sendOTP(phone).fold(
                onSuccess = {
                    _otpSent.value = true
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "خطا در ارسال کد تایید"
                    _loading.value = false
                }
            )
        }
    }
}

