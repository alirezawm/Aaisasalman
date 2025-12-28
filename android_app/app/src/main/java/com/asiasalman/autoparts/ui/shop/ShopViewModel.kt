package com.asiasalman.autoparts.ui.shop

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.ProductsResponse
import com.asiasalman.autoparts.data.repository.ProductRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ShopViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {
    
    private val _products = MutableLiveData<List<com.asiasalman.autoparts.data.model.Product>>()
    val products: LiveData<List<com.asiasalman.autoparts.data.model.Product>> = _products
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadProducts(page: Int = 1) {
        viewModelScope.launch {
            _loading.value = true
            productRepository.getProducts(page = page).fold(
                onSuccess = {
                    _products.value = it.products
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message
                    _loading.value = false
                }
            )
        }
    }
    
    fun searchProducts(query: String) {
        viewModelScope.launch {
            _loading.value = true
            productRepository.searchProducts(query).fold(
                onSuccess = {
                    _products.value = it.products
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message
                    _loading.value = false
                }
            )
        }
    }
}

