package com.asiasalman.mobile.ui.screens.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.asiasalman.mobile.data.model.Brand
import com.asiasalman.mobile.data.model.Category
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.data.repository.Repository
import com.asiasalman.mobile.data.repository.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class SortOption(val displayName: String) {
    RELEVANCE("مرتبط‌ترین"),
    PRICE_LOW_TO_HIGH("ارزان‌ترین"),
    PRICE_HIGH_TO_LOW("گران‌ترین"),
    BEST_SELLING("پرفروش‌ترین"),
    DISCOUNTED("دارای تخفیف")
}

data class SearchFilters(
    val brandId: Int? = null,
    val categoryId: Int? = null,
    val vehicleTypeId: Int? = null,
    val sortBy: SortOption = SortOption.RELEVANCE,
    val onlyDiscounted: Boolean = false,
    val onlyInStock: Boolean = false
)

data class SearchUiState(
    val isLoading: Boolean = false,
    val searchQuery: String = "",
    val products: List<Product> = emptyList(),
    val brands: List<Brand> = emptyList(),
    val categories: List<Category> = emptyList(),
    val filters: SearchFilters = SearchFilters(),
    val showFilters: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SearchUiState())
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()
    
    init {
        loadFiltersData()
    }
    
    private fun loadFiltersData() {
        viewModelScope.launch {
            // Load brands
            when (val result = repository.getBrands()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(brands = result.data)
                }
                else -> { }
            }
            
            // Load categories
            when (val result = repository.getCategories()) {
                is Result.Success -> {
                    _uiState.value = _uiState.value.copy(categories = result.data)
                }
                else -> { }
            }
        }
    }
    
    fun updateSearchQuery(query: String) {
        _uiState.value = _uiState.value.copy(searchQuery = query)
        if (query.isBlank()) {
            _uiState.value = _uiState.value.copy(products = emptyList())
        }
    }
    
    fun search() {
        val query = _uiState.value.searchQuery.trim()
        if (query.isEmpty()) return
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            when (val result = repository.searchProducts(query, 1)) {
                is Result.Success -> {
                    var products = result.data.products
                    
                    // Apply filters
                    products = applyFilters(products)
                    
                    // Apply sorting
                    products = applySorting(products)
                    
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        products = products
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
    
    private fun applyFilters(products: List<Product>): List<Product> {
        val filters = _uiState.value.filters
        var filtered = products
        
        if (filters.brandId != null) {
            filtered = filtered.filter { it.brand?.id == filters.brandId }
        }
        
        if (filters.categoryId != null) {
            filtered = filtered.filter { it.category?.id == filters.categoryId }
        }
        
        if (filters.onlyDiscounted) {
            filtered = filtered.filter { it.discountPercent > 0 }
        }
        
        if (filters.onlyInStock) {
            filtered = filtered.filter { it.inStock && (it.stockQuantity == null || it.stockQuantity!! > 0) }
        }
        
        return filtered
    }
    
    private fun applySorting(products: List<Product>): List<Product> {
        return when (_uiState.value.filters.sortBy) {
            SortOption.PRICE_LOW_TO_HIGH -> {
                products.sortedBy { it.retailPriceCash }
            }
            SortOption.PRICE_HIGH_TO_LOW -> {
                products.sortedByDescending { it.retailPriceCash }
            }
            SortOption.BEST_SELLING -> {
                // Assuming best selling products might have a sales count or rating
                // For now, sort by discount percent as a proxy
                products.sortedByDescending { it.discountPercent }
            }
            SortOption.DISCOUNTED -> {
                products.filter { it.discountPercent > 0 }
                    .sortedByDescending { it.discountPercent }
            }
            else -> products
        }
    }
    
    fun updateFilters(filters: SearchFilters) {
        _uiState.value = _uiState.value.copy(filters = filters)
        if (_uiState.value.searchQuery.isNotEmpty()) {
            search()
        }
    }
    
    fun toggleFilters() {
        _uiState.value = _uiState.value.copy(showFilters = !_uiState.value.showFilters)
    }
    
    fun clearFilters() {
        _uiState.value = _uiState.value.copy(
            filters = SearchFilters(),
            showFilters = false
        )
        if (_uiState.value.searchQuery.isNotEmpty()) {
            search()
        }
    }
    
    fun clearSearch() {
        _uiState.value = _uiState.value.copy(
            searchQuery = "",
            products = emptyList(),
            error = null
        )
    }
}

