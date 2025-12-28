package com.asiasalman.autoparts.ui.product

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.Product
import com.asiasalman.autoparts.data.repository.ProductRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ProductDetailViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {
    
    private val _product = MutableLiveData<Product?>()
    val product: LiveData<Product?> = _product
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadProduct(productId: Int) {
        viewModelScope.launch {
            _loading.value = true
            _error.value = null
            
            productRepository.getProduct(productId).fold(
                onSuccess = {
                    _product.value = it
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "خطا در دریافت محصول"
                    _loading.value = false
                }
            )
        }
    }
}

