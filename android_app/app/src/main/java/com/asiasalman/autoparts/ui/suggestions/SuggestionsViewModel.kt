package com.asiasalman.autoparts.ui.suggestions

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
class SuggestionsViewModel @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _suggestions = MutableLiveData<List<com.asiasalman.autoparts.data.model.Product>>()
    val suggestions: LiveData<List<com.asiasalman.autoparts.data.model.Product>> = _suggestions
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadSuggestions() {
        viewModelScope.launch {
            _loading.value = true
            
            // First try to get from app config
            try {
                val token = tokenManager.getAccessToken()
                val configResponse = apiService.getAppConfig(token?.let { "Bearer $it" })
                if (configResponse.isSuccessful && configResponse.body()?.success == true) {
                    val suggestions = configResponse.body()!!.data!!.dailySuggestions.products
                    if (suggestions.isNotEmpty()) {
                        _suggestions.value = suggestions
                        _loading.value = false
                        return@launch
                    }
                }
            } catch (e: Exception) {
                // Fallback to daily discount products
            }
            
            // Fallback to daily discount products
            try {
                val token = tokenManager.getAccessToken()
                val response = apiService.getDailyDiscountProducts(20, 0, token?.let { "Bearer $it" })
                if (response.isSuccessful && response.body()?.success == true) {
                    _suggestions.value = response.body()!!.data!!.products
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
            
            _loading.value = false
        }
    }
}

