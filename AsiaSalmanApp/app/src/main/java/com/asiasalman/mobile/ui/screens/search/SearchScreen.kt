package com.asiasalman.mobile.ui.screens.search

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.asiasalman.mobile.data.model.Brand
import com.asiasalman.mobile.data.model.Category
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.ui.components.ProductCard
import com.asiasalman.mobile.ui.navigation.Screen
import com.asiasalman.mobile.ui.theme.*
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    navController: NavController,
    viewModel: SearchViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf(uiState.searchQuery) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = { 
                            searchQuery = it
                            viewModel.updateSearchQuery(it)
                        },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = {
                            Text(
                                "جستجوی محصول...",
                                color = TextSecondary
                            )
                        },
                        leadingIcon = {
                            IconButton(onClick = { navController.popBackStack() }) {
                                Icon(Icons.Rounded.ArrowBack, "بازگشت")
                            }
                        },
                        trailingIcon = {
                            Row {
                                if (searchQuery.isNotEmpty()) {
                                    IconButton(onClick = { 
                                        searchQuery = ""
                                        viewModel.clearSearch()
                                    }) {
                                        Icon(Icons.Rounded.Clear, "پاک کردن")
                                    }
                                }
                                IconButton(onClick = { viewModel.search() }) {
                                    Icon(Icons.Rounded.Search, "جستجو")
                                }
                            }
                        },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Primary,
                    titleContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(MaterialTheme.colorScheme.background)
        ) {
            // Filter Chips
            FilterChipsRow(
                filters = uiState.filters,
                viewModel = viewModel,
                onFilterClick = { viewModel.toggleFilters() },
                onClearFilters = { viewModel.clearFilters() },
                modifier = Modifier.fillMaxWidth()
            )
            
            // Results
            when {
                uiState.isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = Primary)
                    }
                }
                
                uiState.error != null -> {
                    ErrorState(
                        message = uiState.error!!,
                        onRetry = { viewModel.search() },
                        modifier = Modifier.fillMaxSize()
                    )
                }
                
                uiState.products.isEmpty() && uiState.searchQuery.isNotEmpty() -> {
                    EmptyState(
                        message = "نتیجه‌ای یافت نشد",
                        modifier = Modifier.fillMaxSize()
                    )
                }
                
                uiState.products.isEmpty() -> {
                    EmptyState(
                        message = "برای جستجو، نام محصول را وارد کنید",
                        modifier = Modifier.fillMaxSize()
                    )
                }
                
                else -> {
                    ProductsGrid(
                        products = uiState.products,
                        user = null, // Can be passed from viewModel if needed
                        onProductClick = { product ->
                            navController.navigate(Screen.ProductDetail.createRoute(product.id))
                        },
                        onAddToCart = { product ->
                            // Handle add to cart
                        }
                    )
                }
            }
        }
        
        // Filter Bottom Sheet
        if (uiState.showFilters) {
            FilterBottomSheet(
                filters = uiState.filters,
                brands = uiState.brands,
                categories = uiState.categories,
                onFiltersChanged = { filters ->
                    viewModel.updateFilters(filters)
                },
                onDismiss = {
                    viewModel.toggleFilters()
                }
            )
        }
    }
    
    // Auto-search with delay
    LaunchedEffect(searchQuery) {
        if (searchQuery.isNotEmpty() && searchQuery.length >= 3) {
            delay(500) // 500ms debounce
            if (searchQuery == uiState.searchQuery) {
                viewModel.search()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterChipsRow(
    filters: SearchFilters,
    viewModel: SearchViewModel,
    onFilterClick: () -> Unit,
    onClearFilters: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 2.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            FilterChip(
                selected = false,
                onClick = onFilterClick,
                leadingIcon = {
                    Icon(Icons.Rounded.Tune, null, modifier = Modifier.size(18.dp))
                },
                label = { Text("فیلترها") }
            )
            
            if (filters.brandId != null || filters.categoryId != null || 
                filters.onlyDiscounted || filters.onlyInStock) {
                FilterChip(
                    selected = true,
                    onClick = onClearFilters,
                    label = { Text("حذف فیلترها") },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Error.copy(alpha = 0.1f)
                    )
                )
            }
            
            // Sort Chip
            var showSortMenu by remember { mutableStateOf(false) }
            Box {
                FilterChip(
                    selected = filters.sortBy != SortOption.RELEVANCE,
                    onClick = { showSortMenu = true },
                    label = { Text("مرتب‌سازی: ${filters.sortBy.displayName}") }
                )
                
                DropdownMenu(
                    expanded = showSortMenu,
                    onDismissRequest = { showSortMenu = false }
                ) {
                    SortOption.values().forEach { option ->
                        DropdownMenuItem(
                            text = { Text(option.displayName) },
                            onClick = {
                                viewModel.updateFilters(filters.copy(sortBy = option))
                                showSortMenu = false
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ProductsGrid(
    products: List<Product>,
    user: com.asiasalman.mobile.data.model.User?,
    onProductClick: (Product) -> Unit,
    onAddToCart: (Product) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        modifier = Modifier.fillMaxSize()
    ) {
        items(products.chunked(2)) { row ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                row.forEach { product ->
                    ProductCard(
                        product = product,
                        user = user,
                        onClick = { onProductClick(product) },
                        onAddToCart = { onAddToCart(product) },
                        modifier = Modifier.weight(1f)
                    )
                }
                // Add empty space if odd number
                if (row.size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterBottomSheet(
    filters: SearchFilters,
    brands: List<Brand>,
    categories: List<Category>,
    onFiltersChanged: (SearchFilters) -> Unit,
    onDismiss: () -> Unit
) {
    var selectedBrandId by remember { mutableStateOf(filters.brandId) }
    var selectedCategoryId by remember { mutableStateOf(filters.categoryId) }
    var onlyDiscounted by remember { mutableStateOf(filters.onlyDiscounted) }
    var onlyInStock by remember { mutableStateOf(filters.onlyInStock) }
    
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = MaterialTheme.colorScheme.surface
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Text(
                text = "فیلترها",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            // Brand Filter
            if (brands.isNotEmpty()) {
                Column {
                    Text(
                        text = "برند",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(brands) { brand ->
                            FilterChip(
                                selected = selectedBrandId == brand.id,
                                onClick = {
                                    selectedBrandId = if (selectedBrandId == brand.id) null else brand.id
                                },
                                label = { Text(brand.nameFa ?: brand.name) }
                            )
                        }
                    }
                }
            }
            
            // Category Filter
            if (categories.isNotEmpty()) {
                Column {
                    Text(
                        text = "دسته‌بندی",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(categories) { category ->
                            FilterChip(
                                selected = selectedCategoryId == category.id,
                                onClick = {
                                    selectedCategoryId = if (selectedCategoryId == category.id) null else category.id
                                },
                                label = { Text(category.name) }
                            )
                        }
                    }
                }
            }
            
            // Options
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = onlyDiscounted,
                        onCheckedChange = { onlyDiscounted = it }
                    )
                    Text("فقط تخفیف‌دار")
                }
                
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = onlyInStock,
                        onCheckedChange = { onlyInStock = it }
                    )
                    Text("فقط موجود")
                }
            }
            
            // Apply Button
            Button(
                onClick = {
                    onFiltersChanged(
                        filters.copy(
                            brandId = selectedBrandId,
                            categoryId = selectedCategoryId,
                            onlyDiscounted = onlyDiscounted,
                            onlyInStock = onlyInStock
                        )
                    )
                    onDismiss()
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = Primary)
            ) {
                Text("اعمال فیلترها")
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun EmptyState(
    message: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(32.dp)
        ) {
            Icon(
                Icons.Rounded.SearchOff,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = TextSecondary
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = TextSecondary
            )
        }
    }
}

@Composable
private fun ErrorState(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(32.dp)
        ) {
            Icon(
                Icons.Rounded.ErrorOutline,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = Error
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = Error
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(
                onClick = onRetry,
                colors = ButtonDefaults.buttonColors(containerColor = Primary)
            ) {
                Icon(Icons.Rounded.Refresh, null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("تلاش مجدد")
            }
        }
    }
}

