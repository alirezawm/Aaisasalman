package com.asiasalman.mobile.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.model.*
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val isLoading: Boolean = false,
    val banners: List<Banner> = emptyList(),
    val sections: List<HomeSection> = emptyList(),
    val sectionProducts: Map<String, List<Product>> = emptyMap(),
    val user: User? = null,
    val error: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            // Load user profile if logged in
            val isLoggedIn = repository.isLoggedIn().first()
            if (isLoggedIn) {
                when (val result = repository.getUserProfile()) {
                    is Result.Success -> {
                        _uiState.value = _uiState.value.copy(user = result.data)
                    }
                    else -> { /* Handle silently */ }
                }
            }
            
            // Load banners
            when (val result = repository.getBanners()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(banners = result.data)
                }
                is Result.Error -> { /* Handle silently */ }
                is Result.Loading -> { }
            }
            
            // Load home sections configuration
            when (val result = repository.getHomeSections()) {
                is Result.Success -> {
                    val sections = result.data
                    _uiState.value = _uiState.value.copy(sections = sections)
                    
                    // Load products for each section
                    loadSectionProducts(sections)
                }
                is Result.Error -> {
                    // Fallback to default sections if API fails
                    val defaultSections = getDefaultSections()
                    _uiState.value = _uiState.value.copy(sections = defaultSections)
                    loadSectionProducts(defaultSections)
                }
                is Result.Loading -> { }
            }
        }
    }
    
    private suspend fun loadSectionProducts(sections: List<HomeSection>) {
        val productsMap = mutableMapOf<String, List<Product>>()
        
        sections.forEach { section ->
            when (val result = repository.getFeaturedProducts(
                featured = section.type,
                page = 1,
                perPage = section.limit
            )) {
                is Result.Success -> {
                    productsMap[section.type] = result.data.products
                }
                else -> {
                    productsMap[section.type] = emptyList()
                }
            }
        }
        
        _uiState.value = _uiState.value.copy(
            isLoading = false,
            sectionProducts = productsMap
        )
    }
    
    private fun getDefaultSections(): List<HomeSection> {
        return listOf(
            HomeSection(
                id = 1,
                type = "bestselling",
                title = "کالاهای پرفروش",
                icon = "fire",
                enabled = true,
                order = 1,
                limit = 10
            ),
            HomeSection(
                id = 2,
                type = "discounted",
                title = "کالاهای تخفیف‌دار",
                icon = "discount",
                enabled = true,
                order = 2,
                limit = 10
            ),
            HomeSection(
                id = 3,
                type = "new",
                title = "کالاهای جدید",
                icon = "star",
                enabled = true,
                order = 3,
                limit = 10
            ),
            HomeSection(
                id = 4,
                type = "special",
                title = "پیشنهادات ویژه",
                icon = "diamond",
                enabled = true,
                order = 4,
                limit = 5
            )
        )
    }
    
    fun refresh() {
        loadData()
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

