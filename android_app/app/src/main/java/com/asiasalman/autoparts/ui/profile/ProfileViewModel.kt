package com.asiasalman.autoparts.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.User
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.data.repository.AuthRepository
import com.asiasalman.autoparts.util.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val apiService: ApiService,
    private val authRepository: AuthRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user
    
    private val _loggedOut = MutableLiveData<Boolean>()
    val loggedOut: LiveData<Boolean> = _loggedOut
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadProfile() {
        viewModelScope.launch {
            _loading.value = true
            val token = tokenManager.getAccessToken()
            if (token != null) {
                try {
                    val response = apiService.getUserProfile("Bearer $token")
                    if (response.isSuccessful && response.body()?.success == true) {
                        _user.value = response.body()!!.data!!.user
                    }
                } catch (e: Exception) {
                    _error.value = e.message
                }
            }
            _loading.value = false
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _loggedOut.value = true
        }
    }
}

