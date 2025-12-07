package com.asiasalman.mobile.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.asiasalman.mobile.ui.theme.*

@Composable
fun PriceDisplay(
    retailCash: Double,
    retailCheck: Double,
    bulkCash: Double? = null,
    bulkCheck: Double? = null,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Retail Prices Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            PriceCard(
                label = "نقدی خرده",
                price = retailCash,
                color = Success,
                icon = Icons.Rounded.Payments,
                modifier = Modifier.weight(1f)
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            PriceCard(
                label = "چکی خرده",
                price = retailCheck,
                color = Primary,
                icon = Icons.Rounded.CreditCard,
                modifier = Modifier.weight(1f)
            )
        }
        
        // Bulk Prices Row (if available)
        if (bulkCash != null || bulkCheck != null) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                bulkCash?.let {
                    PriceCard(
                        label = "نقدی عمده",
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
                    PriceCard(
                        label = "چکی عمده",
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
private fun PriceCard(
    label: String,
    price: Double,
    color: Color,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        ),
        shape = MaterialTheme.shapes.medium
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp),
                    tint = color
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = color
                )
            }
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = formatPrice(price),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
    }
}

private fun formatPrice(price: Double): String {
    return String.format("%,.0f ریال", price)
}

