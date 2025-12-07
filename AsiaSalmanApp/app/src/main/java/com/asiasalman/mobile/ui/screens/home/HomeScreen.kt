package com.asiasalman.mobile.ui.screens.home

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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.asiasalman.mobile.data.model.HomeSection
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.ui.components.BannerCarousel
import com.asiasalman.mobile.ui.components.ProductCard
import com.asiasalman.mobile.ui.components.SectionHeader
import com.asiasalman.mobile.ui.navigation.Screen
import com.asiasalman.mobile.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    navController: NavController,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Header with Gradient Background
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shadowElevation = 8.dp
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(Primary, PrimaryDark)
                        )
                    )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Logo and Company Name
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            Icons.Rounded.Storefront,
                            contentDescription = null,
                            modifier = Modifier.size(32.dp),
                            tint = Color.White
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "آسیا سلمان",
                            style = MaterialTheme.typography.headlineMedium,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Text(
                        text = "فروشگاه قطعات خودرو",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White.copy(alpha = 0.9f)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Search Bar
                    OutlinedTextField(
                        value = "",
                        onValueChange = { },
                        readOnly = true,
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { navController.navigate("search") }
                            .shadow(4.dp, RoundedCornerShape(16.dp)),
                        placeholder = {
                            Text(
                                "جستجوی محصول...",
                                color = TextSecondary
                            )
                        },
                        leadingIcon = {
                            Icon(
                                Icons.Rounded.Search,
                                contentDescription = null,
                                tint = Primary
                            )
                        },
                        singleLine = true,
                        shape = RoundedCornerShape(16.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White,
                            focusedBorderColor = Color.Transparent,
                            unfocusedBorderColor = Color.Transparent
                        )
                    )
                }
            }
        }
        
        // Content
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Banners Section
            if (uiState.banners.isNotEmpty()) {
                item {
                    AnimatedVisibility(
                        visible = uiState.banners.isNotEmpty(),
                        enter = fadeIn() + slideInVertically(),
                        exit = fadeOut()
                    ) {
                        BannerCarousel(
                            banners = uiState.banners,
                            onBannerClick = { banner ->
                                // Handle banner click
                            }
                        )
                    }
                }
            }
            
            // Product Sections (based on configuration)
            items(
                items = uiState.sections,
                key = { it.id }
            ) { section ->
                val products = uiState.sectionProducts[section.type] ?: emptyList()
                
                if (products.isNotEmpty()) {
                    AnimatedVisibility(
                        visible = products.isNotEmpty(),
                        enter = fadeIn() + slideInVertically(
                            initialOffsetY = { it / 2 }
                        ),
                        exit = fadeOut()
                    ) {
                        Column {
                            SectionHeader(
                                title = section.title,
                                icon = getIconForSection(section.icon ?: section.type),
                                onViewAllClick = {
                                    // Navigate to all products of this section
                                }
                            )
                            
                            ProductsHorizontalRow(
                                products = products,
                                user = uiState.user,
                                navController = navController,
                                onProductClick = { product ->
                                    navController.navigate(Screen.ProductDetail.createRoute(product.id))
                                },
                                onAddToCart = { product ->
                                    viewModel.addToCart(product)
                                }
                            )
                        }
                    }
                }
            }
            
            // Loading State
            if (uiState.isLoading && uiState.sections.isEmpty()) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = Primary)
                    }
                }
            }
            
            // Error State
            uiState.error?.let { error ->
                item {
                    ErrorCard(
                        message = error,
                        onRetry = { viewModel.refresh() }
                    )
                }
            }
        }
        
        // Show refresh indicator if loading
        if (uiState.isLoading && uiState.sections.isNotEmpty()) {
            LinearProgressIndicator(
                modifier = Modifier.fillMaxWidth(),
                color = Primary
            )
        }
    }
}

@Composable
private fun ProductsHorizontalRow(
    products: List<Product>,
    user: com.asiasalman.mobile.data.model.User?,
    navController: NavController? = null,
    onProductClick: (Product) -> Unit,
    onAddToCart: (Product) -> Unit
) {
    LazyRow(
        modifier = Modifier.fillMaxWidth(),
        contentPadding = PaddingValues(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(products, key = { it.id }) { product ->
            ProductCard(
                product = product,
                user = user,
                onClick = { onProductClick(product) },
                onAddToCart = { onAddToCart(product) },
                modifier = Modifier.width(170.dp)
            )
        }
    }
}

@Composable
private fun ErrorCard(
    message: String,
    onRetry: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Error.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Rounded.ErrorOutline,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = Error
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = Error
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = onRetry,
                colors = ButtonDefaults.buttonColors(containerColor = Primary)
            ) {
                Icon(
                    Icons.Rounded.Refresh,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("تلاش مجدد")
            }
        }
    }
}

private fun getIconForSection(iconName: String): ImageVector {
    return when (iconName.lowercase()) {
        "fire", "bestselling" -> Icons.Rounded.LocalFireDepartment
        "discount", "discounted" -> Icons.Rounded.Discount
        "star", "new" -> Icons.Rounded.Star
        "diamond", "special" -> Icons.Rounded.Diamond
        else -> Icons.Rounded.Label
    }
}
