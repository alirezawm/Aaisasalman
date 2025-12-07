package com.asiasalman.mobile.ui.screens.splash

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.local.DataStoreManager
import com.asiasalman.mobile.data.local.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SplashUiState(
    val isLoggedIn: Boolean = false,
    val isFirstLaunch: Boolean = true,
    val isLoading: Boolean = true
)

@HiltViewModel
class SplashViewModel @Inject constructor(
    private val tokenManager: TokenManager,
    private val dataStoreManager: DataStoreManager
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SplashUiState())
    val uiState: StateFlow<SplashUiState> = _uiState.asStateFlow()
    
    init {
        checkAuthStatus()
    }
    
    private fun checkAuthStatus() {
        viewModelScope.launch {
            // Check if user is logged in
            val token = tokenManager.getAccessToken()
            val isLoggedIn = !token.isNullOrEmpty()
            
            // Check if it's first launch
            val isFirstLaunch = dataStoreManager.isFirstLaunch.first()
            
            _uiState.value = SplashUiState(
                isLoggedIn = isLoggedIn,
                isFirstLaunch = isFirstLaunch,
                isLoading = false
            )
            
            // Mark first launch as complete
            if (isFirstLaunch) {
                dataStoreManager.setFirstLaunchComplete()
            }
        }
    }
}

