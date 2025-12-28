package com.asiasalman.autoparts.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.asiasalman.autoparts.data.model.Product

@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val nameFa: String,
    val sku: String,
    val oemCode: String?,
    val description: String?,
    val descriptionFa: String?,
    val imageUrl: String,
    val images: String?, // JSON string
    val priceCash: Int,
    val priceCheck: Int,
    val priceCashBulk: Int?,
    val priceCheckBulk: Int?,
    val discountPercentage: Float?,
    val discountedPriceCash: Int?,
    val discountedPriceCheck: Int?,
    val stockQuantity: Int,
    val isActive: Boolean,
    val brandId: Int?,
    val brandName: String?,
    val brandNameFa: String?,
    val brandLogoUrl: String?,
    val categoryId: Int?,
    val categoryName: String?,
    val categoryNameFa: String?,
    val vehicleTypeId: Int?,
    val vehicleTypeName: String?,
    val vehicleTypeNameFa: String?,
    val cachedAt: Long = System.currentTimeMillis()
) {
    fun toProduct(): Product {
        return Product(
            id = id,
            name = name,
            nameFa = nameFa,
            sku = sku,
            oemCode = oemCode,
            description = description,
            descriptionFa = descriptionFa,
            imageUrl = imageUrl,
            images = images?.let { 
                try {
                    com.google.gson.Gson().fromJson(it, Array<String>::class.java).toList()
                } catch (e: Exception) {
                    emptyList()
                }
            },
            priceCash = priceCash,
            priceCheck = priceCheck,
            priceCashBulk = priceCashBulk,
            priceCheckBulk = priceCheckBulk,
            discountPercentage = discountPercentage,
            discountedPriceCash = discountedPriceCash,
            discountedPriceCheck = discountedPriceCheck,
            stockQuantity = stockQuantity,
            isActive = isActive,
            brand = brandId?.let {
                com.asiasalman.autoparts.data.model.Brand(
                    id = it,
                    name = brandName ?: "",
                    nameFa = brandNameFa ?: "",
                    logoUrl = brandLogoUrl
                )
            },
            category = categoryId?.let {
                com.asiasalman.autoparts.data.model.Category(
                    id = it,
                    name = categoryName ?: "",
                    nameFa = categoryNameFa ?: ""
                )
            },
            vehicleType = vehicleTypeId?.let {
                com.asiasalman.autoparts.data.model.VehicleType(
                    id = it,
                    name = vehicleTypeName ?: "",
                    nameFa = vehicleTypeNameFa ?: ""
                )
            },
            productType = null
        )
    }
    
    companion object {
        fun fromProduct(product: Product): ProductEntity {
            return ProductEntity(
                id = product.id,
                name = product.name,
                nameFa = product.nameFa,
                sku = product.sku,
                oemCode = product.oemCode,
                description = product.description,
                descriptionFa = product.descriptionFa,
                imageUrl = product.imageUrl,
                images = product.images?.let { 
                    com.google.gson.Gson().toJson(it)
                },
                priceCash = product.priceCash,
                priceCheck = product.priceCheck,
                priceCashBulk = product.priceCashBulk,
                priceCheckBulk = product.priceCheckBulk,
                discountPercentage = product.discountPercentage,
                discountedPriceCash = product.discountedPriceCash,
                discountedPriceCheck = product.discountedPriceCheck,
                stockQuantity = product.stockQuantity,
                isActive = product.isActive,
                brandId = product.brand?.id,
                brandName = product.brand?.name,
                brandNameFa = product.brand?.nameFa,
                brandLogoUrl = product.brand?.logoUrl,
                categoryId = product.category?.id,
                categoryName = product.category?.name,
                categoryNameFa = product.category?.nameFa,
                vehicleTypeId = product.vehicleType?.id,
                vehicleTypeName = product.vehicleType?.name,
                vehicleTypeNameFa = product.vehicleType?.nameFa
            )
        }
    }
}

