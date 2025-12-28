package com.asiasalman.autoparts.ui.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.autoparts.data.model.*
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.data.remote.Banner
import com.asiasalman.autoparts.util.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _banners = MutableLiveData<List<Banner>>()
    val banners: LiveData<List<Banner>> = _banners
    
    private val _discountedProducts = MutableLiveData<List<Product>>()
    val discountedProducts: LiveData<List<Product>> = _discountedProducts
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    fun loadHomeData() {
        viewModelScope.launch {
            _loading.value = true
            
            // Load banners
            try {
                val bannersResponse = apiService.getBanners("homepage")
                if (bannersResponse.isSuccessful && bannersResponse.body()?.success == true) {
                    _banners.value = bannersResponse.body()!!.data!!.banners
                }
            } catch (e: Exception) {
                // Ignore banner errors
            }
            
            // Load discounted products
            try {
                val token = tokenManager.getAccessToken()
                val productsResponse = apiService.getDailyDiscountProducts(
                    20, 0, token?.let { "Bearer $it" }
                )
                if (productsResponse.isSuccessful && productsResponse.body()?.success == true) {
                    _discountedProducts.value = productsResponse.body()!!.data!!.products
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
            
            _loading.value = false
        }
    }
}

