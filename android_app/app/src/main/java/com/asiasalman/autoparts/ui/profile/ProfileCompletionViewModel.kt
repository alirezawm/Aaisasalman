package com.asiasalman.autoparts.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.util.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileCompletionViewModel @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _profileUpdated = MutableLiveData<Boolean>()
    val profileUpdated: LiveData<Boolean> = _profileUpdated
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun updateProfile(fullName: String, email: String?, companyName: String?) {
        viewModelScope.launch {
            val token = tokenManager.getAccessToken()
            if (token != null) {
                try {
                    val request = com.asiasalman.autoparts.data.remote.UpdateProfileRequest(
                        fullName = fullName,
                        email = email,
                        companyName = companyName
                    )
                    val response = apiService.updateUserProfile(request, "Bearer $token")
                    if (response.isSuccessful && response.body()?.success == true) {
                        _profileUpdated.value = true
                    } else {
                        _error.value = response.body()?.message ?: "خطا در به‌روزرسانی پروفایل"
                    }
                } catch (e: Exception) {
                    _error.value = e.message
                }
            }
        }
    }
}

