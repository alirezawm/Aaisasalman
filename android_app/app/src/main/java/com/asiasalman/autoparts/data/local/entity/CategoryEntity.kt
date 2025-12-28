package com.asiasalman.autoparts.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "categories")
data class CategoryEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val nameFa: String,
    val cachedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "brands")
data class BrandEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val nameFa: String,
    val logoUrl: String?,
    val cachedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "banners")
data class BannerEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val titleFa: String,
    val imageUrl: String,
    val linkUrl: String?,
    val position: String,
    val isActive: Boolean,
    val cachedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "notifications")
data class NotificationEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val message: String,
    val type: String,
    val isRead: Boolean,
    val createdAt: String?,
    val actionUrl: String?,
    val cachedAt: Long = System.currentTimeMillis()
)

