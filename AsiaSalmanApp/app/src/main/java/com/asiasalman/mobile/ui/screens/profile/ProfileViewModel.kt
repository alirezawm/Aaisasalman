package com.asiasalman.mobile.ui.screens.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.local.DataStoreManager
import com.asiasalman.mobile.data.model.User
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProfileUiState(
    val isLoading: Boolean = false,
    val isLoggedIn: Boolean = false,
    val user: User? = null,
    val isDarkMode: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: Repository,
    private val dataStoreManager: DataStoreManager
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()
    
    init {
        checkLoginStatus()
        loadDarkModePreference()
    }
    
    private fun loadDarkModePreference() {
        viewModelScope.launch {
            dataStoreManager.darkMode.collect { isDarkMode ->
                _uiState.value = _uiState.value.copy(isDarkMode = isDarkMode)
            }
        }
    }
    
    fun toggleDarkMode() {
        viewModelScope.launch {
            val current = _uiState.value.isDarkMode
            dataStoreManager.setDarkMode(!current)
        }
    }
    
    private fun checkLoginStatus() {
        viewModelScope.launch {
            repository.isLoggedIn().collect { isLoggedIn ->
                _uiState.value = _uiState.value.copy(isLoggedIn = isLoggedIn)
                if (isLoggedIn) {
                    loadProfile()
                }
            }
        }
    }
    
    private fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            when (val result = repository.getUserProfile()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        user = result.data
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
    
    fun logout() {
        viewModelScope.launch {
            repository.logout()
            _uiState.value = ProfileUiState(isLoggedIn = false)
        }
    }
}

