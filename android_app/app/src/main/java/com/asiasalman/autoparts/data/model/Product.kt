package com.asiasalman.autoparts.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class Product(
    val id: Int,
    val name: String,
    val nameFa: String,
    val sku: String,
    val oemCode: String?,
    val description: String?,
    val descriptionFa: String?,
    val imageUrl: String,
    val images: List<String>?,
    val priceCash: Int,
    val priceCheck: Int,
    val priceCashBulk: Int?,
    val priceCheckBulk: Int?,
    val discountPercentage: Float?,
    val discountedPriceCash: Int?,
    val discountedPriceCheck: Int?,
    val stockQuantity: Int,
    val isActive: Boolean,
    val brand: Brand?,
    val category: Category?,
    val vehicleType: VehicleType?,
    val productType: ProductType?
) : Parcelable {
    fun getDisplayPrice(isCash: Boolean, isBulk: Boolean = false): Int {
        return when {
            discountPercentage != null && discountPercentage > 0 -> {
                if (isCash) discountedPriceCash ?: priceCash
                else discountedPriceCheck ?: priceCheck
            }
            isBulk -> {
                if (isCash) priceCashBulk ?: priceCash
                else priceCheckBulk ?: priceCheck
            }
            else -> {
                if (isCash) priceCash else priceCheck
            }
        }
    }
    
    fun hasDiscount(): Boolean = discountPercentage != null && discountPercentage > 0
    
    fun isInStock(): Boolean = stockQuantity > 0
}

@Parcelize
data class Brand(
    val id: Int,
    val name: String,
    val nameFa: String,
    val logoUrl: String?
) : Parcelable

@Parcelize
data class Category(
    val id: Int,
    val name: String,
    val nameFa: String
) : Parcelable

@Parcelize
data class VehicleType(
    val id: Int,
    val name: String,
    val nameFa: String
) : Parcelable

@Parcelize
data class ProductType(
    val id: Int,
    val name: String,
    val nameFa: String
) : Parcelable

