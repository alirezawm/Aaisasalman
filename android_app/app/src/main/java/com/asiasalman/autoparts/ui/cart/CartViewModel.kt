package com.asiasalman.autoparts.ui.cart

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.Cart
import com.asiasalman.autoparts.data.repository.CartRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CartViewModel @Inject constructor(
    private val cartRepository: CartRepository
) : ViewModel() {
    
    private val _cart = MutableLiveData<Cart?>()
    val cart: LiveData<Cart?> = _cart
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadCart() {
        viewModelScope.launch {
            _loading.value = true
            cartRepository.getCart().fold(
                onSuccess = {
                    _cart.value = it
                    _loading.value = false
                },
                onFailure = { exception ->
                    _error.value = exception.message
                    _loading.value = false
                }
            )
        }
    }
    
    fun updateQuantity(cartItemId: Int, quantity: Int) {
        viewModelScope.launch {
            cartRepository.updateCartItem(cartItemId, quantity).fold(
                onSuccess = {
                    loadCart() // Reload cart
                },
                onFailure = { exception ->
                    _error.value = exception.message
                }
            )
        }
    }
    
    fun removeItem(cartItemId: Int) {
        viewModelScope.launch {
            cartRepository.removeFromCart(cartItemId).fold(
                onSuccess = {
                    loadCart() // Reload cart
                },
                onFailure = { exception ->
                    _error.value = exception.message
                }
            )
        }
    }
    
    private val _cartAdded = MutableLiveData<Boolean>()
    val cartAdded: LiveData<Boolean> = _cartAdded
    
    fun addToCart(productId: Int, quantity: Int, priceType: String) {
        viewModelScope.launch {
            cartRepository.addToCart(productId, quantity, priceType).fold(
                onSuccess = {
                    _cartAdded.value = true
                    loadCart() // Reload cart
                },
                onFailure = { exception ->
                    _error.value = exception.message
                    _cartAdded.value = false
                }
            )
        }
    }
}

