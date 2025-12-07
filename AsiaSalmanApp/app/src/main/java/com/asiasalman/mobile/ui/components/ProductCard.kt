package com.asiasalman.mobile.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.asiasalman.mobile.data.model.Product
import com.asiasalman.mobile.data.model.User
import com.asiasalman.mobile.ui.theme.*

@Composable
fun ProductCard(
    product: Product,
    onClick: () -> Unit,
    onAddToCart: () -> Unit,
    user: User? = null,
    modifier: Modifier = Modifier
) {
    val isBulkBuyer = user?.isBulkBuyer == true
    val showFourPrices = isBulkBuyer && 
        (product.bulkPriceCash != null || product.bulkPriceCheck != null)
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // Product Image
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
            ) {
                AsyncImage(
                    model = product.primaryImage,
                    contentDescription = product.name,
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp)),
                    contentScale = ContentScale.Crop
                )
                
                // Discount Badge
                if (product.discountPercent > 0) {
                    Surface(
                        modifier = Modifier
                            .padding(8.dp)
                            .align(Alignment.TopStart),
                        color = Primary,
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Rounded.Discount,
                                contentDescription = null,
                                modifier = Modifier.size(14.dp),
                                tint = Color.White
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "${product.discountPercent}%",
                                color = Color.White,
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
                
                // Stock indicator
                if (product.stockQuantity != null) {
                    Surface(
                        modifier = Modifier
                            .padding(8.dp)
                            .align(Alignment.TopEnd),
                        color = when {
                            product.stockQuantity == 0 -> Error.copy(alpha = 0.9f)
                            product.stockQuantity!! < 5 -> Warning.copy(alpha = 0.9f)
                            else -> Color.Transparent
                        },
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        if (product.stockQuantity == 0) {
                            Text(
                                text = "ناموجود",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                color = Color.White,
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }
                }
            }
            
            Column(modifier = Modifier.padding(12.dp)) {
                // Product Name
                Text(
                    text = product.name,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                // Brand
                product.brand?.let { brand ->
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = brand.nameFa ?: brand.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Prices
                if (showFourPrices) {
                    // Display 4 prices for bulk buyers
                    PriceDisplay(
                        retailCash = product.retailPriceCash,
                        retailCheck = product.retailPriceCheck,
                        bulkCash = product.bulkPriceCash,
                        bulkCheck = product.bulkPriceCheck
                    )
                } else {
                    // Display 2 prices for regular users
                    PriceDisplay(
                        retailCash = product.retailPriceCash,
                        retailCheck = product.retailPriceCheck
                    )
                }
                
                Spacer(modifier = Modifier.height(10.dp))
                
                // Add to Cart Button
                Button(
                    onClick = onAddToCart,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = product.stockQuantity == null || product.stockQuantity!! > 0,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Primary,
                        disabledContainerColor = Primary.copy(alpha = 0.5f)
                    ),
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(10.dp)
                ) {
                    Icon(
                        Icons.Rounded.AddShoppingCart,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (product.stockQuantity == 0) "ناموجود" else "افزودن به سبد",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
private fun PriceDisplay(
    retailCash: Double,
    retailCheck: Double,
    bulkCash: Double? = null,
    bulkCheck: Double? = null
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        // Retail prices (always shown)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            PriceRow(
                label = "نقدی",
                price = retailCash,
                color = Success,
                icon = Icons.Rounded.Payments,
                modifier = Modifier.weight(1f)
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            PriceRow(
                label = "چکی",
                price = retailCheck,
                color = Primary,
                icon = Icons.Rounded.CreditCard,
                modifier = Modifier.weight(1f)
            )
        }
        
        // Bulk prices (if available)
        if (bulkCash != null || bulkCheck != null) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                bulkCash?.let {
                    PriceRow(
                        label = "عمده نقدی",
                        price = it,
                        color = Accent,
                        icon = Icons.Rounded.AccountBalance,
                        modifier = Modifier.weight(1f)
                    )
                }
                
                if (bulkCash != null && bulkCheck != null) {
                    Spacer(modifier = Modifier.width(8.dp))
                }
                
                bulkCheck?.let {
                    PriceRow(
                        label = "عمده چکی",
                        price = it,
                        color = Secondary,
                        icon = Icons.Rounded.Business,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
private fun PriceRow(
    label: String,
    price: Double,
    color: Color,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 2.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(12.dp),
                tint = color
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = color
            )
        }
        Text(
            text = formatPrice(price),
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

private fun formatPrice(price: Double): String {
    return String.format("%,.0f", price)
}

