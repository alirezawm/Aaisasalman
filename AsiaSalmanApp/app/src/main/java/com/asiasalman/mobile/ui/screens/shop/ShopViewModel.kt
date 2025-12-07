package com.asiasalman.mobile.ui.screens.shop

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.model.Banner
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ShopUiState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val discountedProducts: List<Product> = emptyList(),
    val banners: List<Banner> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class ShopViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ShopUiState())
    val uiState: StateFlow<ShopUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            // Load banners
            when (val result = repository.getBanners()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(banners = result.data)
                }
                is Result.Error -> { /* Handle silently */ }
                is Result.Loading -> { }
            }
            
            // Load discounted products
            when (val result = repository.getDiscountedProducts()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        discountedProducts = result.data.products
                    )
                }
                is Result.Error -> { /* Handle silently */ }
                is Result.Loading -> { }
            }
            
            // Load all products
            when (val result = repository.getProducts()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        products = result.data.products
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
    
    fun search(query: String) {
        if (query.isBlank()) {
            loadData()
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            when (val result = repository.searchProducts(query)) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        products = result.data.products
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
}

