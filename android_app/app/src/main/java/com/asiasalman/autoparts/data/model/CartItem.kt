package com.asiasalman.autoparts.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class CartItem(
    val id: Int,
    val product: Product,
    val quantity: Int,
    val unitPriceCash: Int?,
    val unitPriceCheck: Int?,
    val totalPriceCash: Int,
    val totalPriceCheck: Int,
    val priceType: String, // "cash" or "check"
    val pricePlan: String?
) : Parcelable {
    fun getTotalPrice(isCash: Boolean): Int {
        return if (isCash) totalPriceCash else totalPriceCheck
    }
    
    fun getUnitPrice(isCash: Boolean): Int {
        return if (isCash) (unitPriceCash ?: 0) else (unitPriceCheck ?: 0)
    }
}

@Parcelize
data class Cart(
    val cashCart: CartSection,
    val checkCart: CartSection,
    val grandTotal: Int,
    val totalItems: Int
) : Parcelable

@Parcelize
data class CartSection(
    val items: List<CartItem>,
    val total: Int,
    val itemCount: Int
) : Parcelable

