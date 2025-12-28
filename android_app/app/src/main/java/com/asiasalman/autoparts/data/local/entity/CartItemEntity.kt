package com.asiasalman.autoparts.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.asiasalman.autoparts.data.model.CartItem

@Entity(tableName = "cart_items")
data class CartItemEntity(
    @PrimaryKey val id: Int,
    val productId: Int,
    val productName: String,
    val productNameFa: String,
    val productImageUrl: String,
    val productSku: String,
    val quantity: Int,
    val unitPriceCash: Int?,
    val unitPriceCheck: Int?,
    val totalPriceCash: Int,
    val totalPriceCheck: Int,
    val priceType: String, // "cash" or "check"
    val pricePlan: String?,
    val cachedAt: Long = System.currentTimeMillis()
) {
    fun toCartItem(product: com.asiasalman.autoparts.data.model.Product): CartItem {
        return CartItem(
            id = id,
            product = product,
            quantity = quantity,
            unitPriceCash = unitPriceCash,
            unitPriceCheck = unitPriceCheck,
            totalPriceCash = totalPriceCash,
            totalPriceCheck = totalPriceCheck,
            priceType = priceType,
            pricePlan = pricePlan
        )
    }
}

