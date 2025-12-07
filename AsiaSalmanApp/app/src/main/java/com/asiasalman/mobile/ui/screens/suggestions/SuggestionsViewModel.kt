package com.asiasalman.mobile.ui.screens.suggestions

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SuggestionsUiState(
    val isLoading: Boolean = false,
    val suggestions: List<Product> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class SuggestionsViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SuggestionsUiState())
    val uiState: StateFlow<SuggestionsUiState> = _uiState.asStateFlow()
    
    init {
        loadSuggestions()
    }
    
    fun loadSuggestions() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = repository.getDailySuggestions()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        suggestions = result.data
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
    
    fun addToCart(product: Product) {
        viewModelScope.launch {
            repository.addToCart(
                productId = product.id,
                quantity = 1,
                priceType = "cash"
            )
        }
    }
}

